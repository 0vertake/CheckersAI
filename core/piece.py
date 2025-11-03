def is_valid_position(row, col):
    return 0 <= row < 8 and 0 <= col < 8


class Piece:
    EMPTY = 0
    RED = 1
    BLUE = 2
    RED_KING = 3
    BLUE_KING = 4
    
    @staticmethod
    def is_red(piece):
        return piece in (Piece.RED, Piece.RED_KING)
    
    @staticmethod
    def is_blue(piece):
        return piece in (Piece.BLUE, Piece.BLUE_KING)
    
    @staticmethod
    def is_king(piece):
        return piece in (Piece.RED_KING, Piece.BLUE_KING)
    
    @staticmethod
    def make_king(piece):
        if piece == Piece.RED:
            return Piece.RED_KING
        elif piece == Piece.BLUE:
            return Piece.BLUE_KING
        return piece
    
    @staticmethod
    def get_color(piece):
        if Piece.is_red(piece):
            return "RED"
        elif Piece.is_blue(piece):
            return "BLUE"
        return None


def board_to_cache_key(board):
    key = ""
    for row in board:
        for cell in row:
            if cell == Piece.RED:
                key += "r"
            elif cell == Piece.BLUE:
                key += "b"
            elif cell == Piece.RED_KING:
                key += "R"
            elif cell == Piece.BLUE_KING:
                key += "B"
            else:
                key += "0"
    return key


def cache_key_to_board(key):
    board = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
    for i in range(64):
        row = i // 8
        col = i % 8
        if key[i] == "r":
            board[row][col] = Piece.RED
        elif key[i] == "b":
            board[row][col] = Piece.BLUE
        elif key[i] == "R":
            board[row][col] = Piece.RED_KING
        elif key[i] == "B":
            board[row][col] = Piece.BLUE_KING
    return board
