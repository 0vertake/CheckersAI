from core.board import Board
from ui.gui import CheckersGUI
from game.ai import CheckersAI
from utils.cache import save_cache, cache
import pygame


class GameLogic:

    def __init__(self, must_jump):

        self.must_jump = must_jump
        self.board = Board(self.must_jump)
        self.gui = CheckersGUI(self.board, must_jump)
        self.ai = CheckersAI(self)

    def start(self):

        running = True
        message = ""
        bot_thinking = False
        
        while running:
            winner = self.check_winner()
            if winner != "NONE":
                self.gui.current_player = winner
                self.gui.render(f"{winner} wins!")
                pygame.time.wait(500)
                self.gui.show_game_over(winner)
                running = False
                break
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and not bot_thinking:
                    if self.gui.current_player == "BLUE":
                        move_made = self.gui.handle_click(event.pos)
                        
                        if move_made:
                            winner = self.check_winner()
                            if winner != "NONE":
                                continue
                                
                            self.gui.current_player = "RED"
                            message = "Bot is thinking..."
                            bot_thinking = True
                            
            self.gui.render(message)
            
            if bot_thinking:
                pygame.time.wait(300)
                self.ai.bot_move()
                save_cache(cache, self.must_jump)
                bot_thinking = False
                message = ""
                self.gui.current_player = "BLUE"
                self.gui.selected_piece = None
                self.gui.valid_moves = []
                self.gui.valid_jumps = []
                
        self.gui.quit()

    def check_winner(self):

        if (self.board.red_pieces == 0 and self.board.red_kings == 0) or not self.board.get_all_moves("RED", self.must_jump):
            return "BLUE"
        elif (self.board.blue_pieces == 0 and self.board.blue_kings == 0) or not self.board.get_all_moves("BLUE", self.must_jump):
            return "RED"
        return "NONE"
