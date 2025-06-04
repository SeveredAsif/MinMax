import pygame
import sys
import time
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
LOG_FILE = "game_log.txt"

# === Colors ===
DARK_BLUE = (10, 10, 40)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)

# === Drawing Functions ===

def draw_board(screen, board, message=None):
    screen.fill(DARK_BLUE)
    font = pygame.font.SysFont(None, 28)

    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(screen, WHITE, rect, 1)

            cell = board.grid[row][col]
            if cell.count > 0:
                color = RED if cell.color == colors.RED else BLUE
                orb_radius = 6
                spacing = orb_radius * 2 + 4
                max_per_row = CELL_WIDTH // spacing
                for i in range(cell.count):
                    cx = rect.left + 10 + (i % max_per_row) * spacing
                    cy = rect.top + 10 + (i // max_per_row) * spacing
                    pygame.draw.circle(screen, color, (cx, cy), orb_radius)

    if message:
        text = font.render(message, True, WHITE)
        screen.blit(text, (10, 10))

    pygame.display.flip()

def save_board_to_file(board, label="Move"):
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

def get_cell_from_mouse(pos):
    x, y = pos
    return y // CELL_HEIGHT, x // CELL_WIDTH

# === Main Game Loop ===

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chain Reaction")
    clock = pygame.time.Clock()

    board = Board.Board()
    current_player = colors.RED  # Human is RED
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

                if cell.color == 0 or cell.color == current_player:
                    start_time = time.time()
                    board.make_move(current_player, row, col)
                    elapsed = time.time() - start_time
                    print(f"⏱️ Human move time: {elapsed:.2f} seconds")

                    save_board_to_file(board, "Human Move:")
                    draw_board(screen, board)

                    if is_terminal(board):
                        result = who_won(board)
                        winner = "Red wins!" if result > 0 else "Blue wins!" if result < 0 else "Draw!"
                        save_board_to_file(board, "Human Move:")
                        show_message_and_exit(screen, winner)

                    # === AI Move ===
                    draw_board(screen, board, "AI is thinking...")
                    pygame.display.flip()

                    start_time = time.time()
                    moves = valid_moves(board, ai_player)
                    best_value = int(1e9)
                    best_move = None

                    for move in moves:
                        sim_board = result_board(board, move, ai_player)
                        value = minmax(sim_board, 2, -int(1e9), int(1e9), current_player)
                        if value < best_value:
                            best_value = value
                            best_move = move

                    ai_elapsed = time.time() - start_time
                    print(f"🤖 AI move time: {ai_elapsed:.2f} seconds")

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
