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


def load_cache():
    cache = {}
    with open("cache.txt", "r") as file:
        for line in file:
            key, evaluation, must_jump = line.split("|")
            cache[key] = (float(evaluation), must_jump)
    return cache


def save_cache(cache, must_jump):
    with open("cache.txt", "w") as file:
        for key in cache:
            file.write(f"{key}|{cache[key][0]}|{must_jump}\n")


cache = load_cache()


class Board:
    # Evaluation weight constants
    KING_VALUE = 3
    ADVANCEMENT_WEIGHT = 1.0
    CENTRAL_CONTROL_BONUS = 2.0
    EDGE_BONUS = 0.5
    MOBILITY_WEIGHT = 0.1
    
    # Strategic positions
    CENTRAL_POSITIONS = frozenset([
        (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
        (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6)
    ])

    def __init__(self, must_jump):
        self.red_pieces = 12
        self.blue_pieces = 12
        self.red_kings = 0
        self.blue_kings = 0
        self.must_jump = must_jump
        self.board = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
        self.cache = {}
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = Piece.RED
                    elif row > 4:
                        self.board[row][col] = Piece.BLUE

    def copy(self):
        new_board = Board(self.must_jump)
        new_board.board = [row[:] for row in self.board]
        new_board.red_pieces = self.red_pieces
        new_board.red_kings = self.red_kings
        new_board.blue_pieces = self.blue_pieces
        new_board.blue_kings = self.blue_kings
        return new_board

    def get_moves_for_piece(self, piece, row, col):
        moves = []
        directions = []
        if piece == Piece.RED:
            directions.extend([(1, -1), (1, 1)])
        elif piece == Piece.BLUE:
            directions.extend([(-1, -1), (-1, 1)])
        elif Piece.is_king(piece):
            directions.extend([(1, -1), (1, 1), (-1, -1), (-1, 1)])
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if is_valid_position(new_row, new_col) and self.board[new_row][new_col] == Piece.EMPTY:
                moves.append((new_row, new_col))

        return moves

    def get_jumps_for_piece(self, piece, row, col):
        directions = []
        if Piece.is_red(piece):
            directions.extend([(1, -1), (1, 1)])
        if Piece.is_blue(piece):
            directions.extend([(-1, -1), (-1, 1)])
        if Piece.is_king(piece):
            if Piece.is_red(piece):
                directions.extend([(-1, -1), (-1, 1)])
            else:
                directions.extend([(1, -1), (1, 1)])

        def find_jumps(row, col, current_path, current_piece):
            found_jumps = []
            for dr, dc in directions:
                middle_row, middle_col = row + dr, col + dc
                jump_row, jump_col = row + 2 * dr, col + 2 * dc
                if is_valid_position(middle_row, middle_col) and is_valid_position(jump_row, jump_col):
                    middle_piece = self.board[middle_row][middle_col]
                    new_pos = (jump_row, jump_col)
                    if Piece.is_blue(current_piece):
                        if Piece.is_red(middle_piece) and self.board[jump_row][jump_col] == Piece.EMPTY:
                            if new_pos not in current_path:
                                next_path = current_path + [new_pos]

                                if jump_row == 0 and not Piece.is_king(current_piece):
                                    new_piece = Piece.BLUE_KING
                                else:
                                    new_piece = current_piece

                                sub_jumps = find_jumps(jump_row, jump_col, next_path, new_piece)
                                if sub_jumps:
                                    found_jumps.extend(sub_jumps)
                                else:
                                    found_jumps.append(next_path)

                    elif Piece.is_red(current_piece):
                        if Piece.is_blue(middle_piece) and self.board[jump_row][jump_col] == Piece.EMPTY:
                            if new_pos not in current_path:
                                next_path = current_path + [new_pos]
                                if jump_row == 7 and not Piece.is_king(current_piece):
                                    new_piece = Piece.RED_KING
                                else:
                                    new_piece = current_piece

                                sub_jumps = find_jumps(jump_row, jump_col, next_path, new_piece)
                                if sub_jumps:
                                    found_jumps.extend(sub_jumps)
                                else:
                                    found_jumps.append(next_path)
            return found_jumps

        all_jumps = find_jumps(row, col, [(row, col)], piece)
        return all_jumps

    def get_all_moves_for_piece(self, piece, row, col):
        return self.get_moves_for_piece(piece, row, col), self.get_jumps_for_piece(piece, row, col)

    def get_all_moves(self, color, must_jump):
        moves = {}
        jumps = {}
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != Piece.EMPTY:
                    piece_color = Piece.get_color(piece)
                    if piece_color == color:
                        piece_moves, piece_jumps = self.get_all_moves_for_piece(piece, row, col)
                        if piece_moves:
                            moves[(row, col)] = piece_moves
                        if piece_jumps:
                            jumps[(row, col)] = piece_jumps
        if must_jump and jumps:
            moves = {}
        return moves, jumps
    
    def _evaluate_piece_position(self, piece, row, col):
        score = 0.0
        is_on_edge = col == 0 or col == 7
        is_on_board_edge = is_on_edge or row == 0 or row == 7
        is_central = (row, col) in self.CENTRAL_POSITIONS
        
        if piece == Piece.RED:
            # Reward red pieces for advancing toward blue's side
            score += row * self.ADVANCEMENT_WEIGHT
            if is_central:
                score += self.CENTRAL_CONTROL_BONUS
            elif is_on_edge:
                score += self.EDGE_BONUS
                
        elif piece == Piece.RED_KING:
            score += self.KING_VALUE
            if is_central:
                score += self.CENTRAL_CONTROL_BONUS
            elif is_on_board_edge:
                score += self.EDGE_BONUS
                
        elif piece == Piece.BLUE:
            # Reward blue pieces for advancing toward red's side
            score += (7 - row) * self.ADVANCEMENT_WEIGHT
            if is_central:
                score += self.CENTRAL_CONTROL_BONUS
            elif is_on_edge:
                score += self.EDGE_BONUS
                
        elif piece == Piece.BLUE_KING:
            score += self.KING_VALUE
            if is_central:
                score += self.CENTRAL_CONTROL_BONUS
            elif is_on_board_edge:
                score += self.EDGE_BONUS
        
        return score
    
    def _calculate_mobility(self, color, must_jump):
        moves, jumps = self.get_all_moves(color, must_jump)
        total_moves = sum(len(move_list) for move_list in moves.values())
        total_jumps = sum(len(jump_list) for jump_list in jumps.values())
        return total_moves + total_jumps

    def evaluate(self, must_jump):
        # Check cache first
        cache_key = board_to_cache_key(self.board)
        if cache_key in cache:
            return cache[cache_key][0]
        
        # Material evaluation
        red_score = self.red_pieces + (self.red_kings * self.KING_VALUE)
        blue_score = self.blue_pieces + (self.blue_kings * self.KING_VALUE)
        
        # Positional evaluation
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != Piece.EMPTY:
                    piece_score = self._evaluate_piece_position(piece, row, col)
                    if Piece.is_red(piece):
                        red_score += piece_score
                    else:
                        blue_score += piece_score
        
        # Mobility evaluation
        red_mobility = self._calculate_mobility("RED", must_jump)
        blue_mobility = self._calculate_mobility("BLUE", must_jump)
        red_score += red_mobility * self.MOBILITY_WEIGHT
        blue_score += blue_mobility * self.MOBILITY_WEIGHT
        
        # Calculate final evaluation
        evaluation = red_score - blue_score
        self.add_cache(evaluation)
        
        return evaluation

    def play_move(self, start_pos, end_pos, print_move=False):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col]
        self.board[start_row][start_col] = Piece.EMPTY
        if print_move:
            print(f"Piece at ({start_row}, {start_col}) moves to ({end_row}, {end_col}).")
        if piece == Piece.RED and end_row == 7:
            piece = Piece.RED_KING
            self.red_pieces -= 1
            self.red_kings += 1
        elif piece == Piece.BLUE and end_row == 0:
            piece = Piece.BLUE_KING
            self.blue_pieces -= 1
            self.blue_kings += 1
        self.board[end_row][end_col] = piece

    def play_jump(self, jump_sequence, print_move=False):
        if len(jump_sequence) < 2:
            return
        
        for i in range(len(jump_sequence) - 1):
            start_row, start_col = jump_sequence[i]
            end_row, end_col = jump_sequence[i + 1]
            
            piece = self.board[start_row][start_col]
            if print_move:
                print(f"Piece at ({start_row}, {start_col}) jumps to ({end_row}, {end_col}).")
            
            # Remove the jumped piece
            mid_row, mid_col = (start_row + end_row) // 2, (start_col + end_col) // 2
            mid_piece = self.board[mid_row][mid_col]
            if mid_piece == Piece.RED:
                self.red_pieces -= 1
            elif mid_piece == Piece.BLUE:
                self.blue_pieces -= 1
            elif mid_piece == Piece.RED_KING:
                self.red_kings -= 1
            elif mid_piece == Piece.BLUE_KING:
                self.blue_kings -= 1
            self.board[mid_row][mid_col] = Piece.EMPTY
            
            # Move the piece
            self.board[start_row][start_col] = Piece.EMPTY
            
            # Check for king promotion
            if piece == Piece.RED and end_row == 7:
                piece = Piece.RED_KING
                self.red_pieces -= 1
                self.red_kings += 1
            elif piece == Piece.BLUE and end_row == 0:
                piece = Piece.BLUE_KING
                self.blue_pieces -= 1
                self.blue_kings += 1
            
            self.board[end_row][end_col] = piece

    def add_cache(self, evaluation):
        if board_to_cache_key(self.board) in cache:
            return
        cache[board_to_cache_key(self.board)] = (evaluation, self.must_jump)
