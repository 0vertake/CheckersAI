class CheckersAI:

    def __init__(self, game_logic):
        self.game_logic = game_logic

    def minimax(self, board, depth, alpha, beta, maximizer):
        if depth == 0 or self.game_logic.check_winner() != "NONE":
            return board.evaluate(self.game_logic.must_jump), None

        if maximizer:
            max_eval = float('-inf')
            best_move = None
            moves, jumps = board.get_all_moves("RED", self.game_logic.must_jump)
            move_dict = jumps if jumps else moves
            for start_pos, move_list in move_dict.items():
                for move_data in move_list:
                    board_copy = board.copy()
                    if jumps:
                        board_copy.play_jump(move_data)
                    else:
                        board_copy.play_move(start_pos, move_data)
                    evaluation = self.minimax(board_copy, depth - 1, alpha, beta, False)[0]
                    if evaluation > max_eval:
                        max_eval = evaluation
                        best_move = (start_pos, move_data)
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            moves, jumps = board.get_all_moves("BLUE", self.game_logic.must_jump)
            move_dict = jumps if jumps else moves
            for start_pos, move_list in move_dict.items():
                for move_data in move_list:
                    board_copy = board.copy()
                    if jumps:
                        board_copy.play_jump(move_data)
                    else:
                        board_copy.play_move(start_pos, move_data)
                    evaluation = self.minimax(board_copy, depth - 1, alpha, beta, True)[0]
                    if evaluation < min_eval:
                        min_eval = evaluation
                        best_move = (start_pos, move_data)
                    beta = min(beta, evaluation)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
            return min_eval, best_move

    def bot_move(self):
        max_depth = 6
        min_depth = 4
        total_pieces = self.game_logic.board.red_pieces + self.game_logic.board.red_kings + self.game_logic.board.blue_pieces + self.game_logic.board.blue_kings
        initial_pieces = 24
        depth = min_depth + round((1 - total_pieces / initial_pieces) * (max_depth - min_depth))
        print(f"Bot thinking at depth {depth}...")
        evaluation, best_move = self.minimax(self.game_logic.board, depth, float('-inf'), float('inf'), True)
        if best_move:
            start_pos, move_data = best_move
            moves, jumps = self.game_logic.board.get_all_moves("RED", self.game_logic.must_jump)
            if jumps and start_pos in jumps:
                self.game_logic.board.play_jump(move_data, True)
            elif moves and start_pos in moves:
                self.game_logic.board.play_move(start_pos, move_data, True)
