from board import *
from checkersGUI import CheckersGUI
import pygame


class GameLogic:

    def __init__(self, must_jump):

        self.must_jump = must_jump
        self.board = Board(self.must_jump)
        self.gui = CheckersGUI(self.board, must_jump)

    def start(self):

        running = True
        message = ""
        bot_thinking = False
        
        while running:
            # Check for winner
            winner = self.check_winner()
            if winner != "NONE":
                self.gui.current_player = winner
                self.gui.render(f"{winner} wins!")
                pygame.time.wait(500)
                self.gui.show_game_over(winner)
                running = False
                break
                
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and not bot_thinking:
                    if self.gui.current_player == "BLUE":
                        move_made = self.gui.handle_click(event.pos)
                        
                        if move_made:
                            # Check for winner after player move
                            winner = self.check_winner()
                            if winner != "NONE":
                                continue
                                
                            # Switch to bot's turn
                            self.gui.current_player = "RED"
                            message = "Bot is thinking..."
                            bot_thinking = True
                            
            # Render the board
            self.gui.render(message)
            
            # Bot move (after rendering to show "thinking" message)
            if bot_thinking:
                pygame.time.wait(300)  # Small delay so user can see the board state
                self.bot_move()
                save_cache(cache, self.must_jump)
                bot_thinking = False
                message = ""
                self.gui.current_player = "BLUE"
                
        self.gui.quit()

    def check_winner(self):

        if (self.board.red_pieces == 0 and self.board.red_kings == 0) or not self.board.get_all_moves("RED", self.must_jump):
            return "BLUE"
        elif (self.board.blue_pieces == 0 and self.board.blue_kings == 0) or not self.board.get_all_moves("BLUE", self.must_jump):
            return "RED"
        return "NONE"

    def minimax(self, board, depth, alpha, beta, maximizer):
        if depth == 0 or self.check_winner() != "NONE":
            return board.evaluate(self.must_jump), None

        if maximizer:
            max_eval = float('-inf')
            best_move = None
            moves, jumps = board.get_all_moves("RED", self.must_jump)
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
            moves, jumps = board.get_all_moves("BLUE", self.must_jump)
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
        total_pieces = self.board.red_pieces + self.board.red_kings + self.board.blue_pieces + self.board.blue_kings
        initial_pieces = 24
        depth = min_depth + round((1 - total_pieces / initial_pieces) * (max_depth - min_depth))
        print(f"Bot thinking at depth {depth}...")
        evaluation, best_move = self.minimax(self.board, depth, float('-inf'), float('inf'), True)
        if best_move:
            start_pos, move_data = best_move
            moves, jumps = self.board.get_all_moves("RED", self.must_jump)
            if jumps and start_pos in jumps:
                self.board.play_jump(move_data, True)
            elif moves and start_pos in moves:
                self.board.play_move(start_pos, move_data, True)
