import pygame
import sys
import Board
import colors
from minmax import *
from utils import *

# === Game Config ===
WIDTH, HEIGHT = 500, 500
ROWS, COLS = 9, 6
CELL_WIDTH = WIDTH // COLS
CELL_HEIGHT = HEIGHT // ROWS
FPS = 60
FONT_SIZE = 36
LOG_FILE = "game_log.txt"

# === Colors ===
DARK_BLUE = (10, 10, 40)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)

# === Helper Functions ===

def draw_board(screen, board):
    screen.fill(DARK_BLUE)
    font = pygame.font.SysFont(None, FONT_SIZE)

    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(screen, WHITE, rect, 1)

            cell = board.grid[row][col]
            if cell.count > 0:
                color = RED if cell.color == colors.RED else BLUE
                text = font.render(str(cell.count), True, color)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    pygame.display.flip()

def get_cell_from_mouse(pos):
    x, y = pos
    return y // CELL_HEIGHT, x // CELL_WIDTH

def save_board_to_file(board, label="Human Move:"):
    with open(LOG_FILE, "w") as f:
        f.write(f"{label}\n{str(board)}\n")

def show_message_and_exit(screen, message):
    font = pygame.font.SysFont(None, 64)
    text = font.render(message, True, WHITE)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

# === Main Game Loop ===

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chain Reaction")
    clock = pygame.time.Clock()

    board = Board.Board()
    current_player = colors.RED  # Human always plays RED here
    ai_player = colors.BLUE

    draw_board(screen, board)

    while True:
        clock.tick(FPS)
        draw_board(screen, board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_board_to_file(board, "Game interrupted")
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                row, col = get_cell_from_mouse(event.pos)
                cell = board.grid[row][col]

                # Human move validation
                if cell.color == 0 or cell.color == current_player:
                    board.make_move(current_player, row, col)
                    save_board_to_file(board, "Human Move:")
                    draw_board(screen, board)

                    if is_terminal(board):
                        result = who_won(board)
                        winner = "Red wins!" if result > 0 else "Blue wins!" if result < 0 else "Draw!"
                        print(winner)
                        save_board_to_file(board, "Human Move:")
                        show_message_and_exit(screen, winner)

                    # === AI Move ===
                    print("AI is thinking...")
                    moves = valid_moves(board, ai_player)
                    best_value = int(1e9)
                    best_move = None

                    for move in moves:
                        sim_board = result_board(board, move, ai_player)
                        value = minmax(sim_board, 2, -int(1e9), int(1e9), current_player)
                        if value < best_value:
                            best_value = value
                            best_move = move

                    if best_move:
                        board.make_move(ai_player, best_move[0], best_move[1])
                        save_board_to_file(board, "AI Move:")
                        draw_board(screen, board)

                        if is_terminal(board):
                            result = who_won(board)
                            winner = "Red wins!" if result > 0 else "Blue wins!" if result < 0 else "Draw!"
                            save_board_to_file(board, "AI Move:")
                            show_message_and_exit(screen, winner)

if __name__ == "__main__":
    main()
