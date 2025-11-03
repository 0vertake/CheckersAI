import pygame
from core.piece import Piece


class CheckersGUI:

    def __init__(self, board, must_jump):

        pygame.init()
        self.BOARD_SIZE = 8
        self.SQUARE_SIZE = 100
        self.STATUS_HEIGHT = 60
        self.WINDOW_SIZE = self.BOARD_SIZE * self.SQUARE_SIZE
        self.WINDOW_HEIGHT = self.WINDOW_SIZE + self.STATUS_HEIGHT
        self.PIECE_RADIUS = self.SQUARE_SIZE // 3
        self.CROWN_SIZE = self.SQUARE_SIZE // 6
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.BLUE_PIECE = (70, 130, 180)
        self.RED_PIECE = (220, 20, 60)
        self.HIGHLIGHT_COLOR = (255, 255, 0, 100)
        self.VALID_MOVE_COLOR = (144, 238, 144, 150)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Checkers Game")
        self.clock = pygame.time.Clock()
        self.board = board
        self.must_jump = must_jump
        self.selected_piece = None
        self.valid_moves = []
        self.valid_jumps = []
        self.current_player = "BLUE"
        
    def draw_board(self):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                x = col * self.SQUARE_SIZE
                y = row * self.SQUARE_SIZE
                if (row + col) % 2 == 0:
                    color = self.LIGHT_SQUARE
                else:
                    color = self.DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece != Piece.EMPTY:
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    if Piece.is_blue(piece):
                        color = self.BLUE_PIECE
                    else:
                        color = self.RED_PIECE
                    pygame.draw.circle(self.screen, self.BLACK, (x, y), self.PIECE_RADIUS + 3)
                    pygame.draw.circle(self.screen, color, (x, y), self.PIECE_RADIUS)
                    if Piece.is_king(piece):
                        self.draw_crown(x, y)
                        
    def draw_crown(self, x, y):
        crown_color = (255, 215, 0)
        crown_width = self.CROWN_SIZE * 2
        crown_height = self.CROWN_SIZE
        points = [(x - crown_width // 2, y + crown_height // 2), (x - crown_width // 4, y - crown_height // 2), 
                  (x, y + crown_height // 2), (x + crown_width // 4, y - crown_height // 2), (x + crown_width // 2, y + crown_height // 2)]
        pygame.draw.polygon(self.screen, crown_color, points)
        pygame.draw.polygon(self.screen, self.BLACK, points, 2)
        
    def draw_highlights(self):
        if self.selected_piece:
            row, col = self.selected_piece
            x = col * self.SQUARE_SIZE
            y = row * self.SQUARE_SIZE
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(self.HIGHLIGHT_COLOR)
            self.screen.blit(s, (x, y))
        for move_pos in self.valid_moves:
            row, col = move_pos
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(s, self.VALID_MOVE_COLOR, (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), self.SQUARE_SIZE // 4)
            self.screen.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))
        for jump_sequence in self.valid_jumps:
            last_pos = jump_sequence[-1]
            row, col = last_pos
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(s, self.VALID_MOVE_COLOR, (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), self.SQUARE_SIZE // 4)
            self.screen.blit(s, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))
    
    def draw_status(self, message=""):
        status_y = self.WINDOW_SIZE
        status_surface = pygame.Surface((self.WINDOW_SIZE, self.STATUS_HEIGHT))
        status_surface.fill((200, 200, 200))
        self.screen.blit(status_surface, (0, status_y))
        
        font = pygame.font.Font(None, 40)
        turn_text = f"{self.current_player}'s Turn"
        text_surface = font.render(turn_text, True, self.BLACK)
        text_rect = text_surface.get_rect(center=(self.WINDOW_SIZE // 2, status_y + self.STATUS_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        
        if message:
            small_font = pygame.font.Font(None, 24)
            msg_surface = small_font.render(message, True, self.BLACK)
            self.screen.blit(msg_surface, (10, 10))
            
    def render(self, message=""):
        self.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        self.draw_status(message)
        pygame.display.flip()
        self.clock.tick(60)
        
    def get_clicked_square(self, mouse_pos):
        x, y = mouse_pos
        col = x // self.SQUARE_SIZE
        row = y // self.SQUARE_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
        
    def handle_click(self, pos):
        clicked_square = self.get_clicked_square(pos)
        if not clicked_square:
            return None
        
        row, col = clicked_square
        piece = self.board.board[row][col]
        
        if not self.selected_piece:
            if piece != Piece.EMPTY:
                if self.current_player == "BLUE" and Piece.is_blue(piece):
                    self.selected_piece = clicked_square
                    all_moves, all_jumps = self.board.get_all_moves(self.current_player, self.must_jump)
                    if self.must_jump and all_jumps:
                        self.valid_moves = []
                        self.valid_jumps = all_jumps.get(clicked_square, [])
                    else:
                        self.valid_moves = all_moves.get(clicked_square, [])
                        self.valid_jumps = all_jumps.get(clicked_square, [])
            return None
        else:
            if piece != Piece.EMPTY:
                if self.current_player == "BLUE" and Piece.is_blue(piece):
                    self.selected_piece = clicked_square
                    all_moves, all_jumps = self.board.get_all_moves(self.current_player, self.must_jump)
                    if self.must_jump and all_jumps:
                        self.valid_moves = []
                        self.valid_jumps = all_jumps.get(clicked_square, [])
                    else:
                        self.valid_moves = all_moves.get(clicked_square, [])
                        self.valid_jumps = all_jumps.get(clicked_square, [])
                    return None
            
            move_made = False
            if clicked_square in self.valid_moves:
                self.board.play_move(self.selected_piece, clicked_square, True)
                move_made = True
            else:
                for jump_sequence in self.valid_jumps:
                    if clicked_square == jump_sequence[-1]:
                        self.board.play_jump(jump_sequence, True)
                        move_made = True
                        break
            
            self.selected_piece = None
            self.valid_moves = []
            self.valid_jumps = []
            return move_made
            
    def show_game_over(self, winner):
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 72)
        text = font.render(f"{winner} WINS!", True, self.WHITE)
        text_rect = text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        small_font = pygame.font.Font(None, 36)
        instruction = small_font.render("Click to close", True, self.WHITE)
        instruction_rect = instruction.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(instruction, instruction_rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    
    def quit(self):
        pygame.quit()
