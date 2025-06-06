import pygame # type: ignore
import sys
import time
import math
import Board
import colors
from minmax import *
from utils import *

# === Game Config ===
WIDTH, HEIGHT = 800, 600
GAME_WIDTH = 600
SIDEBAR_WIDTH = 200
ROWS, COLS = 9, 6
CELL_WIDTH = GAME_WIDTH // COLS
CELL_HEIGHT = HEIGHT // ROWS
FPS = 60
LOG_FILE = "game_log.txt"

# === Beautiful Colors ===
DARK_BG = (15, 15, 25)
SIDEBAR_BG = (20, 20, 35)
GRID_LINE = (40, 40, 60)
CELL_BG = (25, 25, 40)
CELL_HOVER = (35, 35, 55)
WHITE = (255, 255, 255)
RED = (255, 75, 85)
BLUE = (75, 150, 255)
GREEN = (75, 255, 150)
GOLD = (255, 215, 0)
GRAY = (120, 120, 130)

# === Game State ===
class GameState:
    def __init__(self):
        self.human_start_time = None
        self.human_think_time = 0
        self.ai_think_time = 0
        self.move_count = 0
        self.game_start_time = time.time()
        self.ai_thinking = False
        self.hover_cell = None
        self.animation_time = 0

game_state = GameState()

# === Drawing Functions ===

def draw_gradient_rect(surface, color1, color2, rect):
    """Draw a gradient rectangle"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), 
                        (rect.x, rect.y + y), 
                        (rect.x + rect.width, rect.y + y))

def draw_glowing_circle(surface, color, pos, radius, glow_radius=None):
    """Draw a circle with glow effect"""
    if glow_radius is None:
        glow_radius = radius + 5
    
    # Draw glow layers
    for i in range(3):
        glow_color = (*color, max(0, 60 - i * 20))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius - i)
        surface.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Draw main orb
    pygame.draw.circle(surface, color, pos, radius)
    # Add highlight
    highlight_pos = (pos[0] - radius//3, pos[1] - radius//3)
    pygame.draw.circle(surface, tuple(min(255, c + 80) for c in color), highlight_pos, radius//3)

def draw_board(screen, board):
    # Draw main game area background
    game_rect = pygame.Rect(0, 0, GAME_WIDTH, HEIGHT)
    draw_gradient_rect(screen, DARK_BG, (25, 25, 45), game_rect)
    
    # Draw grid
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
            
            # Cell background with hover effect
            cell_color = CELL_HOVER if game_state.hover_cell == (row, col) else CELL_BG
            pygame.draw.rect(screen, cell_color, rect)
            pygame.draw.rect(screen, GRID_LINE, rect, 2)
            
            # Draw orbs with animation
            cell = board.grid[row][col]
            if cell.count > 0:
                color = RED if cell.color == colors.RED else BLUE
                orb_radius = 8
                spacing = 20
                
                # Calculate orb positions in a nice pattern
                positions = []
                if cell.count == 1:
                    positions = [(rect.centerx, rect.centery)]
                elif cell.count == 2:
                    positions = [
                        (rect.centerx - spacing//2, rect.centery),
                        (rect.centerx + spacing//2, rect.centery)
                    ]
                elif cell.count == 3:
                    positions = [
                        (rect.centerx, rect.centery - spacing//2),
                        (rect.centerx - spacing//2, rect.centery + spacing//4),
                        (rect.centerx + spacing//2, rect.centery + spacing//4)
                    ]
                else:  # 4 or more
                    for i in range(min(cell.count, 4)):
                        angle = (i * 2 * math.pi / 4) + game_state.animation_time * 2
                        pos_x = rect.centerx + math.cos(angle) * 15
                        pos_y = rect.centery + math.sin(angle) * 15
                        positions.append((int(pos_x), int(pos_y)))
                
                # Draw orbs with glow
                for i, pos in enumerate(positions):
                    # Add slight animation offset
                    anim_offset = math.sin(game_state.animation_time * 3 + i) * 2
                    animated_pos = (pos[0], pos[1] + int(anim_offset))
                    draw_glowing_circle(screen, color, animated_pos, orb_radius)

def draw_sidebar(screen, board, current_player):
    # Sidebar background
    sidebar_rect = pygame.Rect(GAME_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    draw_gradient_rect(screen, SIDEBAR_BG, (30, 30, 50), sidebar_rect)
    
    font_large = pygame.font.Font(None, 32)
    font_medium = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 20)
    
    y_offset = 20
    
    # Title
    title = font_large.render("Chain Reaction", True, WHITE)
    screen.blit(title, (GAME_WIDTH + 10, y_offset))
    y_offset += 50
    
    # Current player indicator
    player_color = RED if current_player == colors.RED else BLUE
    player_name = "Your Turn" if current_player == colors.RED else "AI Turn"
    
    # Draw player indicator with glow
    pygame.draw.circle(screen, player_color, (GAME_WIDTH + 30, y_offset + 10), 12)
    pygame.draw.circle(screen, WHITE, (GAME_WIDTH + 30, y_offset + 10), 12, 2)
    
    player_text = font_medium.render(player_name, True, WHITE)
    screen.blit(player_text, (GAME_WIDTH + 50, y_offset))
    y_offset += 40
    
    # Game stats
    stats = [
        f"Move: {game_state.move_count}",
        f"Human Time: {game_state.human_think_time:.1f}s",
        f"AI Time: {game_state.ai_think_time:.1f}s",
        f"Game Time: {time.time() - game_state.game_start_time:.0f}s"
    ]
    
    for stat in stats:
        text = font_small.render(stat, True, GRAY)
        screen.blit(text, (GAME_WIDTH + 10, y_offset))
        y_offset += 25
    
    # AI thinking indicator
    if game_state.ai_thinking:
        y_offset += 20
        thinking_text = font_medium.render("AI Thinking...", True, GOLD)
        screen.blit(thinking_text, (GAME_WIDTH + 10, y_offset))
        
        # Animated thinking dots
        dots = "." * (int(game_state.animation_time * 2) % 4)
        dots_text = font_medium.render(dots, True, GOLD)
        screen.blit(dots_text, (GAME_WIDTH + 120, y_offset))
        y_offset += 30
        
        # Progress bar
        progress_width = SIDEBAR_WIDTH - 20
        progress_rect = pygame.Rect(GAME_WIDTH + 10, y_offset, progress_width, 10)
        pygame.draw.rect(screen, GRID_LINE, progress_rect)
        
        # Animated progress
        progress = (math.sin(game_state.animation_time * 3) + 1) / 2
        fill_width = int(progress * progress_width)
        fill_rect = pygame.Rect(GAME_WIDTH + 10, y_offset, fill_width, 10)
        pygame.draw.rect(screen, BLUE, fill_rect)
    
    # Instructions at bottom
    y_offset = HEIGHT - 100
    instructions = [
        "Click to place orb",
        "Chain reactions win!",
        "Red vs Blue"
    ]
    
    for instruction in instructions:
        text = font_small.render(instruction, True, GRAY)
        screen.blit(text, (GAME_WIDTH + 10, y_offset))
        y_offset += 20

def save_board_to_file(board, label="Move"):
    with open(LOG_FILE, "w") as f:
        f.write(f"{label}\n{str(board)}\n")

def show_game_over(screen, message):
    # Create overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Winner text
    font = pygame.font.Font(None, 72)
    text = font.render(message, True, GOLD)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(text, rect)
    
    # Stats
    font_small = pygame.font.Font(None, 32)
    stats_text = f"Game lasted {game_state.move_count} moves in {time.time() - game_state.game_start_time:.0f} seconds"
    stats = font_small.render(stats_text, True, WHITE)
    stats_rect = stats.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(stats, stats_rect)
    
    # Continue instruction
    continue_text = font_small.render("Game will exit in 3 seconds...", True, GRAY)
    continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    screen.blit(continue_text, continue_rect)
    
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

def get_cell_from_mouse(pos):
    x, y = pos
    if x >= GAME_WIDTH:  # Click in sidebar
        return None
    return y // CELL_HEIGHT, x // CELL_WIDTH

# === AI Functions (Using Original Minmax) ===

def get_best_ai_move(board, ai_player, current_player, depth=2):
    """AI move selection using original minmax function"""
    moves = valid_moves(board, ai_player)
    if not moves:
        return None
    
    best_value = int(1e9)
    best_move = None
    
    for move in moves:
        undo_info = make_move_with_undo_information(board,move,ai_player)
        #sim_board = result_board(board, move, ai_player)
        value = minmax(board, 2, -int(1e9), int(1e9), current_player)
        undo_move(board,undo_info)
        if value < best_value:
            best_value = value
            best_move = move
    
    return best_move

# === Main Game Loop ===

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chain Reaction - Beautiful Edition")
    clock = pygame.time.Clock()

    board = Board.Board()
    current_player = colors.RED  # Human is RED
    ai_player = colors.BLUE

    while True:
        dt = clock.tick(FPS) / 1000.0
        game_state.animation_time += dt
        
        # Handle mouse hover
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] < GAME_WIDTH:
            hover_result = get_cell_from_mouse(mouse_pos)
            game_state.hover_cell = hover_result
        else:
            game_state.hover_cell = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_board_to_file(board, "Game interrupted")
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell_pos = get_cell_from_mouse(event.pos)
                if cell_pos is None:  # Clicked in sidebar
                    continue
                    
                row, col = cell_pos
                cell = board.grid[row][col]

                if cell.color == 0 or cell.color == current_player:
                    # Calculate human thinking time
                    if game_state.human_start_time:
                        game_state.human_think_time = time.time() - game_state.human_start_time
                        game_state.human_start_time = None
                    
                    # INSTANT human move - no lag
                    logged = [[False for _ in range(6)] for _ in range(9)]
                    memory = [[]]
                    board.make_move(current_player, row, col,logged,memory)
                    game_state.move_count += 1
                    save_board_to_file(board, "Human Move:")
                    
                    # Immediately redraw board after human move
                    screen.fill(DARK_BG)
                    draw_board(screen, board)
                    draw_sidebar(screen, board, current_player)
                    pygame.display.flip()

                    if board.is_terminal():
                        result = who_won(board)
                        winner = "You Win!" if result > 0 else "AI Wins!" if result < 0 else "Draw!"
                        show_game_over(screen, winner)

                    # === AI Move with visual feedback ===
                    game_state.ai_thinking = True
                    
                    # Show AI thinking immediately
                    screen.fill(DARK_BG)
                    draw_board(screen, board)
                    draw_sidebar(screen, board, current_player)
                    pygame.display.flip()
                    
                    start_time = time.time()
                    best_move = get_best_ai_move(board, ai_player, current_player, 2)
                    game_state.ai_think_time = time.time() - start_time
                    game_state.ai_thinking = False

                    if best_move:
                        # INSTANT AI move - no lag
                        logged = [[False for _ in range(6)] for _ in range(9)]
                        memory = [[]]
                        board.make_move(ai_player, best_move[0], best_move[1],logged,memory)
                        game_state.move_count += 1
                        save_board_to_file(board, "AI Move:")
                        
                        # Immediately redraw board after AI move
                        screen.fill(DARK_BG)
                        draw_board(screen, board)
                        draw_sidebar(screen, board, current_player)
                        pygame.display.flip()

                        if board.is_terminal():
                            result = who_won(board)
                            winner = "You Win!" if result > 0 else "AI Wins!" if result < 0 else "Draw!"
                            show_game_over(screen, winner)
                    
                    # Reset human timer for next move
                    game_state.human_start_time = time.time()

        # Draw everything
        screen.fill(DARK_BG)
        draw_board(screen, board)
        draw_sidebar(screen, board, current_player)
        pygame.display.flip()

if __name__ == "__main__":
    main()