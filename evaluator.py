"""
Position evaluator for Checkers AI
Provides sophisticated position evaluation for the Minimax algorithm.
"""

class PositionEvaluator:
    def __init__(self):
        """Initialize the position evaluator with evaluation weights"""
        # Piece values
        self.PAWN_VALUE = 100
        self.KING_VALUE = 300
        
        # Positional bonuses
        self.CENTER_CONTROL_BONUS = 10
        self.BACK_RANK_BONUS = 20
        self.SIDE_CONTROL_BONUS = 5
        
        # Advanced evaluation factors
        self.MOBILITY_WEIGHT = 2
        self.CAPTURE_THREAT_WEIGHT = 15
        self.KING_PROMOTION_THREAT_WEIGHT = 25
        
        # Endgame factors
        self.ENDGAME_KING_ADVANTAGE = 50
        self.ENDGAME_MOBILITY_MULTIPLIER = 3
    
    def evaluate(self, board, player):
        """
        Evaluate the current board position
        
        Args:
            board: Board object
            player (str): Player to evaluate for ('red' or 'blue')
            
        Returns:
            int: Position evaluation (positive favors the player)
        """
        if board.is_game_over():
            return self._evaluate_terminal_position(board, player)
        
        # Basic material evaluation
        material_score = self._evaluate_material(board, player)
        
        # Positional evaluation
        positional_score = self._evaluate_position(board, player)
        
        # Mobility evaluation
        mobility_score = self._evaluate_mobility(board, player)
        
        # Threat evaluation
        threat_score = self._evaluate_threats(board, player)
        
        # King promotion evaluation
        promotion_score = self._evaluate_promotion_threats(board, player)
        
        # Combine all factors
        total_score = (material_score + positional_score + 
                      mobility_score + threat_score + promotion_score)
        
        return total_score
    
    def _evaluate_terminal_position(self, board, player):
        """Evaluate terminal game positions"""
        red_pieces = board.count_pieces('red')
        blue_pieces = board.count_pieces('blue')
        
        if red_pieces == 0:
            return -10000 if player == 'red' else 10000
        elif blue_pieces == 0:
            return 10000 if player == 'red' else -10000
        else:
            # No valid moves - stalemate
            return 0
    
    def _evaluate_material(self, board, player):
        """Evaluate material balance"""
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_value = self.KING_VALUE if piece.is_king else self.PAWN_VALUE
                    
                    if piece.color == player:
                        score += piece_value
                    else:
                        score -= piece_value
        
        return score
    
    def _evaluate_position(self, board, player):
        """Evaluate positional factors"""
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == player:
                    # Center control bonus
                    if 2 <= row <= 5 and 2 <= col <= 5:
                        score += self.CENTER_CONTROL_BONUS
                    
                    # Back rank bonus (for kings)
                    if piece.is_king:
                        if player == 'red' and row == 7:
                            score += self.BACK_RANK_BONUS
                        elif player == 'blue' and row == 0:
                            score += self.BACK_RANK_BONUS
                    
                    # Side control bonus
                    if col == 0 or col == 7:
                        score += self.SIDE_CONTROL_BONUS
        
        return score
    
    def _evaluate_mobility(self, board, player):
        """Evaluate piece mobility"""
        moves = board.get_all_moves(player)
        mobility_score = len(moves) * self.MOBILITY_WEIGHT
        
        # Bonus for having multiple capture options
        capture_moves = [move for move in moves if abs(move[1][0] - move[0][0]) == 2]
        mobility_score += len(capture_moves) * self.CAPTURE_THREAT_WEIGHT
        
        return mobility_score
    
    def _evaluate_threats(self, board, player):
        """Evaluate capture threats"""
        threat_score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == player:
                    captures = piece.get_capture_moves(board)
                    threat_score += len(captures) * self.CAPTURE_THREAT_WEIGHT
        
        return threat_score
    
    def _evaluate_promotion_threats(self, board, player):
        """Evaluate king promotion threats"""
        promotion_score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == player and not piece.is_king:
                    # Check if piece is close to promotion
                    if player == 'red' and row <= 2:
                        promotion_score += self.KING_PROMOTION_THREAT_WEIGHT
                    elif player == 'blue' and row >= 5:
                        promotion_score += self.KING_PROMOTION_THREAT_WEIGHT
        
        return promotion_score
    
    def evaluate_move_quality(self, board, move, player):
        """
        Evaluate the quality of a specific move
        
        Args:
            board: Board object
            move (tuple): (from_pos, to_pos) move
            player (str): Player making the move
            
        Returns:
            int: Move evaluation score
        """
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = board.get_piece(from_row, from_col)
        if not piece:
            return 0
        
        score = 0
        
        # Capture bonus
        if abs(to_row - from_row) == 2:
            captured_row = (from_row + to_row) // 2
            captured_col = (from_col + to_col) // 2
            captured_piece = board.get_piece(captured_row, captured_col)
            
            if captured_piece:
                capture_value = self.KING_VALUE if captured_piece.is_king else self.PAWN_VALUE
                score += capture_value
        
        # King promotion bonus
        if not piece.is_king:
            if (player == 'red' and to_row == 0) or (player == 'blue' and to_row == 7):
                score += self.KING_PROMOTION_THREAT_WEIGHT
        
        # Center control bonus
        if 2 <= to_row <= 5 and 2 <= to_col <= 5:
            score += self.CENTER_CONTROL_BONUS
        
        # Mobility bonus
        # Count how many moves the piece will have after this move
        temp_board = board.copy()
        temp_board.move_piece(from_pos, to_pos)
        piece_moves = len(temp_board.get_all_moves(player))
        score += piece_moves * self.MOBILITY_WEIGHT
        
        return score
    
    def get_evaluation_factors(self, board, player):
        """
        Get detailed evaluation breakdown
        
        Args:
            board: Board object
            player (str): Player to evaluate for
            
        Returns:
            dict: Dictionary with evaluation factors
        """
        return {
            'material': self._evaluate_material(board, player),
            'position': self._evaluate_position(board, player),
            'mobility': self._evaluate_mobility(board, player),
            'threats': self._evaluate_threats(board, player),
            'promotion': self._evaluate_promotion_threats(board, player),
            'total': self.evaluate(board, player)
        }
