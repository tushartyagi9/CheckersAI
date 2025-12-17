"""
Piece class for Checkers game
Handles individual piece logic including movement and kinging.
"""

class Piece:
    def __init__(self, color, row, col):
        """
        Initialize a checkers piece
        
        Args:
            color (str): 'red' or 'blue'
            row (int): Row position on board
            col (int): Column position on board
        """
        self.color = color
        self.row = row
        self.col = col
        self.is_king = False
    
    def make_king(self):
        """Promote piece to king"""
        self.is_king = True
    
    def get_possible_moves(self, board):
        """
        Get all possible moves for this piece
        
        Args:
            board: Board object to check for valid moves
            
        Returns:
            list: List of valid move positions
        """
        moves = []
        
        if self.is_king:
            # Kings can move in all four diagonal directions
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            # Regular pieces can only move forward
            if self.color == 'red':
                directions = [(-1, -1), (-1, 1)]  # Red moves up
            else:
                directions = [(1, -1), (1, 1)]    # Blue moves down
        
        for dr, dc in directions:
            new_row = self.row + dr
            new_col = self.col + dc
            
            # Check if position is on board
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = board.get_piece(new_row, new_col)
                
                if target_piece is None:
                    # Empty square - regular move
                    moves.append((new_row, new_col))
                elif target_piece.color != self.color:
                    # Enemy piece - check if we can capture
                    jump_row = new_row + dr
                    jump_col = new_col + dc
                    
                    if (0 <= jump_row < 8 and 0 <= jump_col < 8 and 
                        board.get_piece(jump_row, jump_col) is None):
                        moves.append((jump_row, jump_col))
        
        return moves
    
    def get_capture_moves(self, board):
        """
        Get all possible capture moves for this piece
        
        Args:
            board: Board object to check for valid captures
            
        Returns:
            list: List of valid capture positions
        """
        captures = []
        
        if self.is_king:
            # Kings can capture in all four diagonal directions
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            # Regular pieces can only capture forward
            if self.color == 'red':
                directions = [(-1, -1), (-1, 1)]  # Red captures up
            else:
                directions = [(1, -1), (1, 1)]    # Blue captures down
        
        for dr, dc in directions:
            enemy_row = self.row + dr
            enemy_col = self.col + dc
            
            # Check if enemy position is on board
            if 0 <= enemy_row < 8 and 0 <= enemy_col < 8:
                enemy_piece = board.get_piece(enemy_row, enemy_col)
                
                if enemy_piece and enemy_piece.color != self.color:
                    # Found enemy piece - check if we can jump over it
                    jump_row = enemy_row + dr
                    jump_col = enemy_col + dc
                    
                    if (0 <= jump_row < 8 and 0 <= jump_col < 8 and 
                        board.get_piece(jump_row, jump_col) is None):
                        captures.append((jump_row, jump_col))
        
        return captures
    
    def can_capture(self, board):
        """
        Check if this piece can make any captures
        
        Args:
            board: Board object to check
            
        Returns:
            bool: True if piece can capture
        """
        return len(self.get_capture_moves(board)) > 0
    
    def get_value(self):
        """
        Get the value of this piece for evaluation
        
        Returns:
            int: Piece value (higher for kings)
        """
        return 3 if self.is_king else 1
    
    def copy(self):
        """
        Create a copy of this piece
        
        Returns:
            Piece: Copy of this piece
        """
        new_piece = Piece(self.color, self.row, self.col)
        if self.is_king:
            new_piece.make_king()
        return new_piece
    
    def __str__(self):
        """String representation of the piece"""
        king_symbol = "K" if self.is_king else ""
        return f"{self.color[0].upper()}{king_symbol}"
    
    def __repr__(self):
        """Detailed string representation"""
        return f"Piece({self.color}, {self.row}, {self.col}, king={self.is_king})"
