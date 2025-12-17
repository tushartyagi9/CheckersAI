"""
AI implementation for Checkers using Minimax with alpha-beta pruning
"""

import copy
from evaluator import PositionEvaluator

class AI:
    def __init__(self, depth=4):
        """
        Initialize the AI
        
        Args:
            depth (int): Search depth for Minimax algorithm
        """
        self.depth = depth
        self.evaluator = PositionEvaluator()
        self.nodes_evaluated = 0
        self.pruning_count = 0
    
    def get_best_move(self, board, player):
        """
        Get the best move using Minimax with alpha-beta pruning
        
        Args:
            board: Board object
            player (str): Player color ('red' or 'blue')
            
        Returns:
            dict: Best move with score {'from': (row, col), 'to': (row, col), 'score': int}
        """
        self.nodes_evaluated = 0
        self.pruning_count = 0
        
        moves = board.get_all_moves(player)
        if not moves:
            return None
        
        # If only one move, return it
        if len(moves) == 1:
            return {
                'from': moves[0][0],
                'to': moves[0][1],
                'score': 0
            }
        
        best_move = None
        best_score = float('-inf') if player == 'red' else float('inf')
        
        # Try each possible move
        for move in moves:
            from_pos, to_pos = move
            
            # Make the move on a copy of the board
            temp_board = board.copy()
            temp_board.move_piece(from_pos, to_pos)
            
            # Check for kinging
            piece = temp_board.get_piece(to_pos[0], to_pos[1])
            if piece and not piece.is_king:
                if (player == 'red' and to_pos[0] == 0) or (player == 'blue' and to_pos[0] == 7):
                    piece.make_king()
            
            # Evaluate the position after this move
            score = self._minimax(temp_board, self.depth - 1, 
                                'blue' if player == 'red' else 'red',
                                float('-inf'), float('inf'))
            
            # Update best move
            if player == 'red':
                if score > best_score:
                    best_score = score
                    best_move = {'from': from_pos, 'to': to_pos, 'score': score}
            else:
                if score < best_score:
                    best_score = score
                    best_move = {'from': from_pos, 'to': to_pos, 'score': score}
        
        return best_move
    
    def _minimax(self, board, depth, player, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning
        
        Args:
            board: Board object
            depth (int): Remaining search depth
            player (str): Current player
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            
        Returns:
            int: Best evaluation score
        """
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board, 'red')  # Always evaluate from red's perspective
        
        moves = board.get_all_moves(player)
        if not moves:
            return self.evaluator.evaluate(board, 'red')
        
        if player == 'red':
            # Maximizing player
            max_eval = float('-inf')
            for move in moves:
                from_pos, to_pos = move
                
                # Make move on copy
                temp_board = board.copy()
                temp_board.move_piece(from_pos, to_pos)
                
                # Check for kinging
                piece = temp_board.get_piece(to_pos[0], to_pos[1])
                if piece and not piece.is_king:
                    if to_pos[0] == 0:  # Red kinging
                        piece.make_king()
                
                eval_score = self._minimax(temp_board, depth - 1, 'blue', alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    self.pruning_count += 1
                    break
            
            return max_eval
        else:
            # Minimizing player
            min_eval = float('inf')
            for move in moves:
                from_pos, to_pos = move
                
                # Make move on copy
                temp_board = board.copy()
                temp_board.move_piece(from_pos, to_pos)
                
                # Check for kinging
                piece = temp_board.get_piece(to_pos[0], to_pos[1])
                if piece and not piece.is_king:
                    if to_pos[0] == 7:  # Blue kinging
                        piece.make_king()
                
                eval_score = self._minimax(temp_board, depth - 1, 'red', alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    self.pruning_count += 1
                    break
            
            return min_eval
    
    def get_move_evaluation(self, board, move, player):
        """
        Get evaluation for a specific move
        
        Args:
            board: Board object
            move (tuple): (from_pos, to_pos) move
            player (str): Player making the move
            
        Returns:
            int: Move evaluation score
        """
        from_pos, to_pos = move
        
        # Make move on copy
        temp_board = board.copy()
        temp_board.move_piece(from_pos, to_pos)
        
        # Check for kinging
        piece = temp_board.get_piece(to_pos[0], to_pos[1])
        if piece and not piece.is_king:
            if (player == 'red' and to_pos[0] == 0) or (player == 'blue' and to_pos[0] == 7):
                piece.make_king()
        
        # Evaluate position after move using remaining search depth
        next_player = 'blue' if player == 'red' else 'red'
        search_depth = max(0, self.depth - 1)
        return self._minimax(temp_board, search_depth, next_player, float('-inf'), float('inf'))
    
    def get_best_move_with_analysis(self, board, player):
        """
        Get best move with detailed analysis
        
        Args:
            board: Board object
            player (str): Player color
            
        Returns:
            dict: Move with analysis data
        """
        move = self.get_best_move(board, player)
        if move:
            move['nodes_evaluated'] = self.nodes_evaluated
            move['pruning_count'] = self.pruning_count
            move['efficiency'] = self.pruning_count / max(1, self.nodes_evaluated)
        return move
    
    def get_all_move_evaluations(self, board, player):
        """
        Get evaluations for all possible moves
        
        Args:
            board: Board object
            player (str): Player color
            
        Returns:
            list: List of moves with evaluations
        """
        moves = board.get_all_moves(player)
        evaluated_moves = []
        
        for move in moves:
            from_pos, to_pos = move
            score = self.get_move_evaluation(board, move, player)
            
            evaluated_moves.append({
                'from': from_pos,
                'to': to_pos,
                'score': score
            })
        
        # Sort by score (descending for red, ascending for blue)
        if player == 'red':
            evaluated_moves.sort(key=lambda x: x['score'], reverse=True)
        else:
            evaluated_moves.sort(key=lambda x: x['score'])
        
        return evaluated_moves
    
    def get_search_stats(self):
        """
        Get search statistics
        
        Returns:
            dict: Search statistics
        """
        return {
            'nodes_evaluated': self.nodes_evaluated,
            'pruning_count': self.pruning_count,
            'efficiency': self.pruning_count / max(1, self.nodes_evaluated)
        }
