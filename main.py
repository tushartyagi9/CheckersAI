#!/usr/bin/env python3
"""
Checkers Game with AI Opponent and Move Analysis
A complete implementation of Checkers using Pygame with Minimax AI and move evaluation.
"""

import pygame
import sys
import os
import time
import threading
import subprocess
import platform
import random
from board import Board
from ai import AI
from evaluator import PositionEvaluator
from move_analyzer import MoveAnalyzer
from pdf_generator import PDFReportGenerator

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 8
CELL_SIZE = 80
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + 200  # Extra space for UI
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + 100
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)

class CheckersGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Checkers with AI") 
        self.clock = pygame.time.Clock()
        
        # Game components
        self.board = Board()
        self.ai_player = AI(depth=3)  # Medium AI opponent
        self.assist_ai = AI(depth=5)  # Strong AI for analysis/assistance
        self.evaluator = PositionEvaluator()
        self.move_analyzer = MoveAnalyzer()
        
        # Game state
        self.selected_piece = None
        self.selected_pos = None
        self.current_player = 'red'  # Red starts first (bottom pieces)
        self.game_over = False
        self.winner = None
        
        # Analysis data
        self.move_history = []
        self.analysis_results = []
        
        # Animation and UI state
        self.available_moves = []
        self.ai_thinking = False
        self.ai_thinking_start_time = 0
        self.animating_move = False
        self.animation_start_time = 0
        self.animation_duration = 0.3  # seconds
        self.animation_from = None
        self.animation_to = None
        self.animation_piece = None
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # Game over replay button
        self.replay_button_rect = None
        self.match_review_button_rect = None
        self.position_history = []
        self.is_draw = False
        
        # AI assistance
        self.ai_assistance_button_rect = None
        self.ai_suggestion = None
        self.ai_suggestion_visible = False
        self.ai_suggesting = False
        self.pdf_generator = PDFReportGenerator()
        self.pdf_path = None
        self.player_names = {'red': 'You', 'blue': 'Gukesh'}
        self.resign_button_rect = None
        self.ai_move_delay = 1.0
    
    def serialize_board(self):
        return tuple(tuple((p.color, p.is_king) if p else None for p in row) for row in self.board.board)
    
    def draw_wrapped_text(self, text, x, y, max_width, color):
        """Render multiline text within a max width and return new y"""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            line_surface = self.font.render(line, True, color)
            self.screen.blit(line_surface, (x, y))
            y += self.font.get_linesize()
        return y
    
    def get_player_display_name(self, color):
        if not color:
            return ""
        return self.player_names.get(color, color.title())
    
    def draw_board(self):
        """Draw the checkers board"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                
                # Alternate colors for checkers pattern
                color = LIGHT_BROWN if (row + col) % 2 == 0 else BROWN
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                
                # Highlight selected piece
                if self.selected_pos and self.selected_pos == (row, col):
                    pygame.draw.rect(self.screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE), 3)
                
                # Draw available move indicators
                if (row, col) in self.available_moves:
                    center_x = x + CELL_SIZE // 2
                    center_y = y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), 8)
                    pygame.draw.circle(self.screen, ORANGE, (center_x, center_y), 6)
    
    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    # Skip drawing if this piece is being animated
                    if (self.animating_move and self.animation_piece == piece):
                        continue
                    
                    x = col * CELL_SIZE + CELL_SIZE // 2
                    y = row * CELL_SIZE + CELL_SIZE // 2
                    
                    # Piece color
                    color = RED if piece.color == 'red' else BLUE
                    pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 3)
                    
                    # King crown
                    if piece.is_king:
                        pygame.draw.circle(self.screen, WHITE, (x, y), CELL_SIZE // 6)
                        pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 8)
        
        # Draw animated piece
        if self.animating_move and self.animation_piece:
            self.draw_animated_piece()
    
    def draw_animated_piece(self):
        """Draw piece during animation"""
        if not self.animating_move or not self.animation_piece:
            return
        
        # Calculate animation progress
        elapsed = time.time() - self.animation_start_time
        progress = min(elapsed / self.animation_duration, 1.0)
        
        # Interpolate position
        from_x = self.animation_from[1] * CELL_SIZE + CELL_SIZE // 2
        from_y = self.animation_from[0] * CELL_SIZE + CELL_SIZE // 2
        to_x = self.animation_to[1] * CELL_SIZE + CELL_SIZE // 2
        to_y = self.animation_to[0] * CELL_SIZE + CELL_SIZE // 2
        
        # Smooth animation with easing
        ease_progress = 1 - (1 - progress) ** 2  # Ease out
        
        current_x = from_x + (to_x - from_x) * ease_progress
        current_y = from_y + (to_y - from_y) * ease_progress
        
        # Draw the piece
        color = RED if self.animation_piece.color == 'red' else BLUE
        pygame.draw.circle(self.screen, color, (int(current_x), int(current_y)), CELL_SIZE // 3)
        
        # King crown
        if self.animation_piece.is_king:
            pygame.draw.circle(self.screen, WHITE, (int(current_x), int(current_y)), CELL_SIZE // 6)
            pygame.draw.circle(self.screen, color, (int(current_x), int(current_y)), CELL_SIZE // 8)
        
        # End animation
        if progress >= 1.0:
            self.animating_move = False
            self.animation_piece = None
    
    def draw_game_over_overlay(self):
        """Draw a semi-transparent overlay and a centered game over message"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 144))  # Dim the screen (alpha: 144)
        self.screen.blit(overlay, (0, 0))

        # Draw centered text
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        if self.is_draw:
            game_over_text = "Draw!"
            game_over_surface = self.title_font.render(game_over_text, True, (255, 255, 255))
            self.screen.blit(game_over_surface, (center_x - game_over_surface.get_width() // 2, center_y - 30))
        else:
            game_over_text = "Game Over!"
            winner_label = self.get_player_display_name(self.winner) if self.winner else ""
            winner_text = f"Winner: {winner_label}" if winner_label else ""

            game_over_surface = self.title_font.render(game_over_text, True, (255, 255, 255))
            winner_surface = self.font.render(winner_text, True, (255, 255, 255))

            self.screen.blit(game_over_surface, (center_x - game_over_surface.get_width() // 2, center_y - 60))
            self.screen.blit(winner_surface, (center_x - winner_surface.get_width() // 2, center_y - 10))

        # Draw the replay button
        button_width, button_height = 180, 50
        button_x = center_x - button_width // 2
        button_y = center_y + 50
        self.replay_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (80, 180, 80), self.replay_button_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), self.replay_button_rect, width=2, border_radius=12)
        button_text = self.title_font.render("Replay", True, (255, 255, 255))
        self.screen.blit(button_text, (
            button_x + (button_width - button_text.get_width()) // 2,
            button_y + (button_height - button_text.get_height()) // 2
        ))
        
        # Draw the match review button
        review_button_y = button_y + button_height + 15
        self.match_review_button_rect = pygame.Rect(button_x, review_button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (60, 120, 200), self.match_review_button_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), self.match_review_button_rect, width=2, border_radius=12)
        review_text = self.title_font.render("Match Review", True, (255, 255, 255))
        self.screen.blit(review_text, (
            button_x + (button_width - review_text.get_width()) // 2,
            review_button_y + (button_height - review_text.get_height()) // 2
        ))
    
    def draw_ui(self):
        """Draw game UI elements"""
        ui_rect = pygame.Rect(BOARD_SIZE * CELL_SIZE, 0, 200, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (245, 245, 245), ui_rect)
        pygame.draw.line(self.screen, (220, 220, 220), (BOARD_SIZE * CELL_SIZE, 0), (BOARD_SIZE * CELL_SIZE, WINDOW_HEIGHT), 2)
        ui_x = BOARD_SIZE * CELL_SIZE + 15
        
        # Current player
        player_text = f"Current Player: {self.get_player_display_name(self.current_player)}"
        player_surface = self.font.render(player_text, True, BLACK)
        self.screen.blit(player_surface, (ui_x, 20))
        
        # AI Assistance button (only show during player's turn)
        if not self.game_over and self.current_player == 'red' and not self.ai_thinking:
            button_width, button_height = 160, 40
            button_x = ui_x
            button_y = 60
            self.ai_assistance_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Button color based on state
            if self.ai_suggesting:
                button_color = (100, 150, 200)
            else:
                button_color = (70, 130, 180)
            
            pygame.draw.rect(self.screen, button_color, self.ai_assistance_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), self.ai_assistance_button_rect, width=2, border_radius=8)
            
            button_text_str = "Analyzing..." if self.ai_suggesting else "AI Assistance"
            button_text = self.font.render(button_text_str, True, (255, 255, 255))
            self.screen.blit(button_text, (
                button_x + (button_width - button_text.get_width()) // 2,
                button_y + (button_height - button_text.get_height()) // 2
            ))
            
            # Show AI suggestion if available
            if self.ai_suggestion_visible and self.ai_suggestion:
                suggestion_y = button_y + button_height + 10
                suggestion_text = f"Suggested: {self._format_move(self.ai_suggestion['from'], self.ai_suggestion['to'])}"
                suggestion_surface = self.font.render(suggestion_text, True, GREEN)
                self.screen.blit(suggestion_surface, (ui_x, suggestion_y))
                
                # Highlight suggested move on board
                if self.ai_suggestion:
                    from_pos = self.ai_suggestion['from']
                    to_pos = self.ai_suggestion['to']
                    # Highlight from position
                    from_x = from_pos[1] * CELL_SIZE
                    from_y = from_pos[0] * CELL_SIZE
                    pygame.draw.rect(self.screen, GREEN, (from_x, from_y, CELL_SIZE, CELL_SIZE), 4)
                    # Highlight to position
                    to_x = to_pos[1] * CELL_SIZE
                    to_y = to_pos[0] * CELL_SIZE
                    pygame.draw.rect(self.screen, GREEN, (to_x, to_y, CELL_SIZE, CELL_SIZE), 4)
                    # Draw arrow or line
                    center_from_x = from_x + CELL_SIZE // 2
                    center_from_y = from_y + CELL_SIZE // 2
                    center_to_x = to_x + CELL_SIZE // 2
                    center_to_y = to_y + CELL_SIZE // 2
                    pygame.draw.line(self.screen, GREEN, (center_from_x, center_from_y), (center_to_x, center_to_y), 3)
        else:
            self.ai_assistance_button_rect = None
        
        # Instructions
        instructions = [
            {'text': 'Instructions:', 'header': True},
            {'text': 'Click to select piece'},
            {'text': 'Click destination to move'},
            {'text': 'Click AI Assistance for help'},
            {'text': 'Click Resign to give up'},
            {'text': 'ESC to deselect'},
            {'text': 'R to restart'},
            {'text': 'Q to quit'}
        ]
        
        instructions_y = 140 if not (self.ai_suggestion_visible and self.ai_suggestion) else 180
        instruction_box_height = 210
        pygame.draw.rect(self.screen, (232, 232, 232), (ui_x - 5, instructions_y - 10, 190, instruction_box_height), border_radius=8)
        y_offset = instructions_y
        for item in instructions:
            if item.get('header'):
                text_surface = self.font.render(item['text'], True, BLACK)
                self.screen.blit(text_surface, (ui_x, y_offset))
                y_offset += self.font.get_linesize()
            else:
                y_offset = self.draw_wrapped_text(f"• {item['text']}", ui_x, y_offset, 170, (60, 60, 60))
                y_offset += 4
        
        # Resign button
        if not self.game_over:
            button_width, button_height = 160, 40
            button_x = ui_x
            button_y = y_offset + 10
            self.resign_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(self.screen, (200, 80, 80), self.resign_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), self.resign_button_rect, width=2, border_radius=8)
            resign_text = self.font.render("Resign", True, WHITE)
            self.screen.blit(resign_text, (
                button_x + (button_width - resign_text.get_width()) // 2,
                button_y + (button_height - resign_text.get_height()) // 2
            ))
        else:
            self.resign_button_rect = None
    
    def get_board_position(self, mouse_pos):
        """Convert mouse position to board coordinates"""
        x, y = mouse_pos
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None
    
    def handle_click(self, pos):
        """Handle mouse click events"""
        if self.game_over:
            # Check replay button
            if self.replay_button_rect and self.replay_button_rect.collidepoint(pos):
                self.restart_game()
                return
            # Check match review button
            if self.match_review_button_rect and self.match_review_button_rect.collidepoint(pos):
                self.show_match_review()
                return
        
        # Check AI assistance button
        if self.ai_assistance_button_rect and self.ai_assistance_button_rect.collidepoint(pos):
            if not self.ai_suggesting and not self.game_over and self.current_player == 'red':
                self.get_ai_assistance()
            return
        
        # Check resign button
        if self.resign_button_rect and self.resign_button_rect.collidepoint(pos):
            if not self.game_over:
                self.resign_game()
            return
        
        if self.game_over or self.current_player == 'blue' or self.ai_thinking:  # AI's turn or thinking
            return
        
        board_pos = self.get_board_position(pos)
        if not board_pos:
            return
        
        row, col = board_pos
        
        if self.selected_piece is None:
            # Select a piece
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.current_player:
                self.selected_piece = piece
                self.selected_pos = (row, col)
                # Get available moves for this piece
                self.available_moves = piece.get_possible_moves(self.board)
        else:
            # Try to move the selected piece
            if self.board.is_valid_move(self.selected_pos, board_pos, self.current_player):
                self.make_move(self.selected_pos, board_pos)
            else:
                # Try to select a different piece
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.current_player:
                    self.selected_piece = piece
                    self.selected_pos = (row, col)
                    # Get available moves for this piece
                    self.available_moves = piece.get_possible_moves(self.board)
                else:
                    self.selected_piece = None
                    self.selected_pos = None
                    self.available_moves = []
    
    def make_move(self, from_pos, to_pos):
        """Make a move and switch players"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Record the move
        move = {
            'from': from_pos,
            'to': to_pos,
            'player': self.current_player,
            'move_number': len(self.move_history) + 1
        }
        
        # Analyze the move (before executing it)
        self.analyze_move(move)
        
        # Start animation
        piece = self.board.get_piece(from_row, from_col)
        self.start_animation(piece, from_pos, to_pos)
        
        # Execute the move
        captured = self.board.move_piece(from_pos, to_pos)
        
        # Check for kinging
        piece = self.board.get_piece(to_row, to_col)
        if piece and not piece.is_king:
            if (self.current_player == 'red' and to_row == 0) or \
               (self.current_player == 'blue' and to_row == BOARD_SIZE - 1):
                piece.make_king()
        
        # Add move to history
        move['captured'] = captured
        move['kinged'] = piece.is_king if piece else False
        self.move_history.append(move)
        
        # Clear AI suggestion after move
        self.ai_suggestion = None
        self.ai_suggestion_visible = False
        
        # Check for game over
        if self.check_game_over():
            self.game_over = True
            self.winner = self.get_winner()
        else:
            # Switch players
            self.current_player = 'blue' if self.current_player == 'red' else 'red'
        
        # Clear selection and available moves
        self.selected_piece = None
        self.selected_pos = None
        self.available_moves = []

        # Add board position to history for threefold repetition
        ser = self.serialize_board()
        self.position_history.append(ser)
        if self.position_history.count(ser) >= 3:
            self.game_over = True
            self.is_draw = True
    
    def start_animation(self, piece, from_pos, to_pos):
        """Start piece movement animation"""
        self.animating_move = True
        self.animation_start_time = time.time()
        self.animation_from = from_pos
        self.animation_to = to_pos
        self.animation_piece = piece
    
    def analyze_move(self, move):
        """Analyze the quality of a move"""
        analysis = self.move_analyzer.analyze_move(
            self.board, move, self.evaluator, self.assist_ai
        )
        self.analysis_results.append(analysis)
        # Debug output
        print(f"Move {move['move_number']} ({move['player']}): {move['from']} -> {move['to']}")
        print(f"  Classification: {analysis['classification']}")
        print(f"  Score difference: {analysis['score_difference']:.2f}")
        print(f"  Description: {analysis['description']}")
        print()
    
    def check_game_over(self):
        """Check if the game is over"""
        return self.board.is_game_over()
    
    def get_winner(self):
        """Determine the winner"""
        red_pieces = self.board.count_pieces('red')
        blue_pieces = self.board.count_pieces('blue')
        
        if red_pieces == 0:
            return 'blue'
        elif blue_pieces == 0:
            return 'red'
        elif not self.board.has_valid_moves(self.current_player):
            return 'blue' if self.current_player == 'red' else 'red'
        return None
    
    def ai_move(self):
        """Make AI move with thinking delay"""
        if (self.current_player == 'blue' and not self.game_over and 
            not self.ai_thinking and not self.animating_move):
            # Start AI thinking
            self.ai_thinking = True
            self.ai_thinking_start_time = time.time()
            
            # Use threading to avoid blocking the UI
            def ai_thread():
                # Add thinking delay
                time.sleep(self.ai_move_delay)
                
                # Double-check conditions before making move
                if (self.current_player == 'blue' and not self.game_over and 
                    not self.animating_move):
                    
                    # Get candidate moves for medium difficulty play
                    candidate_moves = self.ai_player.get_all_move_evaluations(self.board, 'blue')
                    selected_move = None
                    if candidate_moves:
                        pool = candidate_moves[:min(4, len(candidate_moves))]
                        weights = list(range(len(pool), 0, -1))  # More weight to stronger moves
                        choice = random.choices(pool, weights=weights, k=1)[0]
                        selected_move = {'from': choice['from'], 'to': choice['to']}
                    else:
                        best_move = self.ai_player.get_best_move(self.board, 'blue')
                        if best_move:
                            selected_move = best_move
                    
                    # Stop thinking
                    self.ai_thinking = False
                    
                    # Make the move
                    if selected_move and self.board.is_valid_move(selected_move['from'], selected_move['to'], 'blue'):
                        self.make_move(selected_move['from'], selected_move['to'])
                    else:
                        # If no valid move, switch to red player
                        self.current_player = 'red'
                        self.ai_thinking = False
                else:
                    # Conditions changed, just stop thinking
                    self.ai_thinking = False
            
            # Start AI thread
            ai_thread_obj = threading.Thread(target=ai_thread)
            ai_thread_obj.daemon = True
            ai_thread_obj.start()
    
    def restart_game(self):
        """Restart the game"""
        self.board = Board()
        self.selected_piece = None
        self.selected_pos = None
        self.current_player = 'red'  # Red starts first (bottom pieces)
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.analysis_results = []
        self.available_moves = []
        self.ai_thinking = False
        self.animating_move = False
        self.position_history = []
        self.is_draw = False
        self.ai_suggestion = None
        self.ai_suggestion_visible = False
        self.ai_suggesting = False
        self.pdf_path = None
        self.resign_button_rect = None
    
    def resign_game(self):
        """Resign the current game"""
        if self.game_over:
            return
        
        resigning_player = self.current_player
        self.game_over = True
        self.is_draw = False
        self.winner = 'blue' if resigning_player == 'red' else 'red'
        self.ai_thinking = False
        print(f"\n🏳️ {self.get_player_display_name(resigning_player)} resigned!")
        print(f"🏆 Winner: {self.get_player_display_name(self.winner)}")
    
    def show_game_summary(self):
        """Display final game summary with detailed evaluation"""
        if not self.game_over:
            return
        
        # Calculate statistics
        red_stats = self.move_analyzer.calculate_player_stats(self.analysis_results, 'red')
        blue_stats = self.move_analyzer.calculate_player_stats(self.analysis_results, 'blue')
        
        print("\n" + "="*80)
        print("🎯 CHECKERS GAME ANALYSIS REPORT")
        print("="*80)
        winner_label = self.get_player_display_name(self.winner)
        print(f"🏆 Winner: {winner_label}" if self.winner else "🎉 Game Drawn!")
        print(f"📊 Total Moves: {len(self.move_history)}")
        print(f"⏱️  Game Duration: {len(self.move_history)} moves")
        print()
        
        human_label = self.get_player_display_name('red')
        ai_label = self.get_player_display_name('blue')
        
        print(f"🧑 {human_label.upper()} (Human) STATISTICS:")
        print(f"  📈 Accuracy: {red_stats['accuracy']:.1f}%")
        print(f"  ✅ Best Moves: {red_stats['best']}")
        print(f"  👍 Good Moves: {red_stats['good']}")
        print(f"  ⚠️  Inaccuracies: {red_stats['inaccuracy']}")
        print(f"  ❌ Blunders: {red_stats['blunder']}")
        print()
        
        print(f"🤖 {ai_label.upper()} (AI) STATISTICS:")
        print(f"  📈 Accuracy: {blue_stats['accuracy']:.1f}%")
        print(f"  ✅ Best Moves: {blue_stats['best']}")
        print(f"  👍 Good Moves: {blue_stats['good']}")
        print(f"  ⚠️  Inaccuracies: {blue_stats['inaccuracy']}")
        print(f"  ❌ Blunders: {blue_stats['blunder']}")
        print()
        
        # Show best moves
        red_best = self.move_analyzer.get_best_moves(self.analysis_results, 'red', 3)
        blue_best = self.move_analyzer.get_best_moves(self.analysis_results, 'blue', 3)
        
        if red_best:
            print(f"🧑 {human_label.upper()} BEST MOVES:")
            for i, move in enumerate(red_best, 1):
                print(f"  {i}. Move {move['move_number']}: {move['from']} → {move['to']}")
            print()
        
        if blue_best:
            print(f"🤖 {ai_label.upper()} BEST MOVES:")
            for i, move in enumerate(blue_best, 1):
                print(f"  {i}. Move {move['move_number']}: {move['from']} → {move['to']}")
            print()
        
        # Show blunders
        red_blunders = self.move_analyzer.get_blunders(self.analysis_results, 'red', 3)
        blue_blunders = self.move_analyzer.get_blunders(self.analysis_results, 'blue', 3)
        
        if red_blunders:
            print(f"🧑 {human_label.upper()} BLUNDERS:")
            for i, move in enumerate(red_blunders, 1):
                print(f"  {i}. Move {move['move_number']}: {move['from']} → {move['to']} (Loss: {move['score_difference']:.1f}cp)")
            print()
        
        if blue_blunders:
            print(f"🤖 {ai_label.upper()} BLUNDERS:")
            for i, move in enumerate(blue_blunders, 1):
                print(f"  {i}. Move {move['move_number']}: {move['from']} → {move['to']} (Loss: {move['score_difference']:.1f}cp)")
            print()
        
        # Overall game quality
        total_best = red_stats['best'] + blue_stats['best']
        total_blunders = red_stats['blunder'] + blue_stats['blunder']
        game_quality = (total_best / len(self.move_history)) * 100 if self.move_history else 0
        
        print("📊 OVERALL GAME QUALITY:")
        print(f"  🎯 Best Move Rate: {game_quality:.1f}%")
        print(f"  ⚡ Blunder Rate: {(total_blunders / len(self.move_history)) * 100:.1f}%" if self.move_history else "  ⚡ Blunder Rate: 0.0%")
        print("="*80)
    
    def _format_move(self, from_pos, to_pos):
        """Format a move for display"""
        from_col = chr(97 + from_pos[1])  # a-h
        from_row = str(8 - from_pos[0])    # 1-8
        to_col = chr(97 + to_pos[1])
        to_row = str(8 - to_pos[0])
        return f"{from_col}{from_row}-{to_col}{to_row}"
    
    def get_ai_assistance(self):
        """Get AI move suggestion for the current player"""
        if self.ai_suggesting or self.game_over or self.current_player != 'red':
            return
        
        self.ai_suggesting = True
        self.ai_suggestion_visible = False
        
        def ai_assistance_thread():
            # Get best move for current player
            best_move = self.assist_ai.get_best_move(self.board, self.current_player)
            if best_move:
                self.ai_suggestion = best_move
                self.ai_suggestion_visible = True
            self.ai_suggesting = False
        
        thread = threading.Thread(target=ai_assistance_thread)
        thread.daemon = True
        thread.start()
    
    def show_match_review(self):
        """Generate and show the match review PDF"""
        if not self.game_over:
            return
        
        try:
            # Generate PDF report
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"checkers_report_{timestamp}.pdf"
            self.pdf_path = self.pdf_generator.generate_report(
                self.move_history,
                self.analysis_results,
                self.winner,
                self.is_draw,
                pdf_filename
            )
            
            print(f"\n📄 PDF Report generated: {self.pdf_path}")
            
            # Open PDF based on platform
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.pdf_path])
            elif platform.system() == 'Windows':
                os.startfile(self.pdf_path)
            else:  # Linux
                subprocess.run(['xdg-open', self.pdf_path])
            
            print("✅ Match review opened!")
            
        except Exception as e:
            print(f"❌ Error generating PDF report: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.selected_piece = None
                        self.selected_pos = None
                        self.available_moves = []
                    elif event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_x:
                        if not self.game_over:
                            self.resign_game()
                    elif event.key == pygame.K_q:
                        running = False
            
            # AI move
            self.ai_move()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_pieces()
            self.draw_ui()
            if self.game_over:
                self.draw_game_over_overlay()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Show final summary
        self.show_game_summary()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CheckersGame()
    game.run()
