"""
Board class for Checkers game
Handles game state, piece management, and move validation.
"""

from piece import Piece

class Board:
    def __init__(self):
        """Initialize an empty board"""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the initial checkers position"""
        # Place red pieces (bottom 3 rows - they move up)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Only dark squares
                    self.board[row][col] = Piece('red', row, col)
        
        # Place blue pieces (top 3 rows - they move down)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:  # Only dark squares
                    self.board[row][col] = Piece('blue', row, col)
    
    def get_piece(self, row, col):
        """
        Get piece at specified position
        
        Args:
            row (int): Row index
            col (int): Column index
            
        Returns:
            Piece or None: Piece at position or None if empty
        """
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """
        Set piece at specified position
        
        Args:
            row (int): Row index
            col (int): Column index
            piece (Piece or None): Piece to place or None to remove
        """
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
            if piece:
                piece.row = row
                piece.col = col
    
    def move_piece(self, from_pos, to_pos):
        """
        Move a piece from one position to another
        
        Args:
            from_pos (tuple): (row, col) of source position
            to_pos (tuple): (row, col) of destination position
            
        Returns:
            Piece or None: Captured piece if any
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        if not piece:
            return None
        
        # Check if this is a capture move
        captured = None
        if abs(to_row - from_row) == 2:  # Jump move
            # Calculate captured piece position
            captured_row = (from_row + to_row) // 2
            captured_col = (from_col + to_col) // 2
            captured = self.board[captured_row][captured_col]
            self.board[captured_row][captured_col] = None
        
        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.row = to_row
        piece.col = to_col
        
        return captured
    
    def is_valid_move(self, from_pos, to_pos, player):
        """
        Check if a move is valid
        
        Args:
            from_pos (tuple): (row, col) of source position
            to_pos (tuple): (row, col) of destination position
            player (str): Player making the move
            
        Returns:
            bool: True if move is valid
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check bounds
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and
                0 <= to_row < 8 and 0 <= to_col < 8):
            return False
        
        piece = self.board[from_row][from_col]
        if not piece or piece.color != player:
            return False
        
        # Check if destination is empty
        if self.board[to_row][to_col] is not None:
            return False
        
        # Check if move is diagonal
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        # Check distance
        distance = abs(to_row - from_row)
        if distance == 1:
            # Regular move - check direction
            if piece.is_king:
                return True
            elif piece.color == 'red' and to_row < from_row:
                return True
            elif piece.color == 'blue' and to_row > from_row:
                return True
        elif distance == 2:
            # Capture move
            captured_row = (from_row + to_row) // 2
            captured_col = (from_col + to_col) // 2
            captured_piece = self.board[captured_row][captured_col]
            
            if captured_piece and captured_piece.color != player:
                return True
        
        return False
    
    def get_all_moves(self, player):
        """
        Get all possible moves for a player
        
        Args:
            player (str): Player color ('red' or 'blue')
            
        Returns:
            list: List of (from_pos, to_pos) tuples
        """
        moves = []
        capture_moves = []
        
        # First, check for capture moves (mandatory)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == player:
                    captures = piece.get_capture_moves(self)
                    for capture_pos in captures:
                        capture_moves.append(((row, col), capture_pos))
        
        # If there are captures, only return captures
        if capture_moves:
            return capture_moves
        
        # Otherwise, return all regular moves
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == player:
                    piece_moves = piece.get_possible_moves(self)
                    for move_pos in piece_moves:
                        moves.append(((row, col), move_pos))
        
        return moves
    
    def has_valid_moves(self, player):
        """
        Check if player has any valid moves
        
        Args:
            player (str): Player color
            
        Returns:
            bool: True if player has valid moves
        """
        return len(self.get_all_moves(player)) > 0
    
    def is_game_over(self):
        """
        Check if the game is over
        
        Returns:
            bool: True if game is over
        """
        red_pieces = self.count_pieces('red')
        blue_pieces = self.count_pieces('blue')
        
        # Game over if no pieces left
        if red_pieces == 0 or blue_pieces == 0:
            return True
        
        # Game over if no valid moves
        if not self.has_valid_moves('red') or not self.has_valid_moves('blue'):
            return True
        
        return False
    
    def count_pieces(self, color):
        """
        Count pieces of a specific color
        
        Args:
            color (str): Piece color ('red' or 'blue')
            
        Returns:
            int: Number of pieces
        """
        count = 0
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    count += 1
        return count
    
    def evaluate_position(self):
        """
        Evaluate the current board position
        
        Returns:
            int: Position evaluation (positive favors red, negative favors blue)
        """
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    piece_value = piece.get_value()
                    if piece.color == 'red':
                        score += piece_value
                    else:
                        score -= piece_value
        
        return score
    
    def copy(self):
        """
        Create a deep copy of the board
        
        Returns:
            Board: Copy of this board
        """
        new_board = Board()
        new_board.board = [[None for _ in range(8)] for _ in range(8)]
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    new_board.board[row][col] = piece.copy()
        
        return new_board
    
    def print_board(self):
        """Print the board to console (for debugging)"""
        print("  " + " ".join(str(i) for i in range(8)))
        for row in range(8):
            print(f"{row} ", end="")
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    print(piece, end=" ")
                else:
                    print(".", end=" ")
            print()
        print()
    
    def get_piece_positions(self, color):
        """
        Get all positions of pieces of a specific color
        
        Args:
            color (str): Piece color
            
        Returns:
            list: List of (row, col) tuples
        """
        positions = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    positions.append((row, col))
        return positions
