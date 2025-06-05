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
PURPLE = (155, 89, 182)
ORANGE = (255, 165, 0)

# === Game Mode Enum ===
class GameMode:
    HUMAN_VS_AI = "Human vs AI"
    AI_VS_AI = "AI vs AI"

class Difficulty:
    EASY = {"name": "Easy", "depth": 1}
    MEDIUM = {"name": "Medium", "depth": 2}
    HARD = {"name": "Hard", "depth": 3}

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
        self.game_mode = GameMode.HUMAN_VS_AI
        self.difficulty = Difficulty.MEDIUM
        self.human_color = colors.RED
        self.ai_color = colors.BLUE
        self.ai_vs_ai_delay = 1.0  # Delay between AI moves for visibility

game_state = GameState()

# === Menu System ===
# class Button:
#     def __init__(self, x, y, width, height, text, color=GRAY, text_color=WHITE, font_size=24):
#         self.rect = pygame.Rect(x, y, width, height)
#         self.text = text
#         self.color = color
#         self.text_color = text_color
#         self.font = pygame.font.Font(None, font_size)
#         self.hovered = False
#         self.selected = False
    
#     def draw(self, screen):
#         # Button background with hover effect
#         color = tuple(min(255, c + 20) for c in self.color) if self.hovered else self.color
#         if self.selected:
#             color = tuple(min(255, c + 40) for c in self.color)
        
#         pygame.draw.rect(screen, color, self.rect)
#         pygame.draw.rect(screen, WHITE, self.rect, 2)
        
#         # Button text
#         text_surf = self.font.render(self.text, True, self.text_color)
#         text_rect = text_surf.get_rect(center=self.rect.center)
#         screen.blit(text_surf, text_rect)
    
#     def is_clicked(self, pos):
#         return self.rect.collidepoint(pos)
    
#     def update_hover(self, pos):
#         self.hovered = self.rect.collidepoint(pos)
class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, text_color=WHITE, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color  # Store original color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.selected = False
        self.clicked = False
        self.click_time = 0
    
    def draw(self, screen):
        # Handle click animation
        if self.clicked and time.time() - self.click_time > 0.1:
            self.clicked = False
        
        # Button background with effects
        if self.clicked:
            # Pressed effect - darker and offset
            color = tuple(max(0, c - 40) for c in self.original_color)
            offset = 2
        else:
            # Normal or hover effect
            if self.hovered or self.selected:
                color = tuple(min(255, c + 40) for c in self.original_color)
            else:
                color = self.original_color
            offset = 0
        
        # Draw button with pressed offset effect
        pressed_rect = self.rect.copy()
        pressed_rect.y += offset
        pygame.draw.rect(screen, color, pressed_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, pressed_rect, 2, border_radius=5)
        
        # Button text with pressed offset
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=pressed_rect.center)
        screen.blit(text_surf, text_rect)
    
    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = True
            self.click_time = time.time()
            return True
        return False
    
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

def show_main_menu(screen):
    """Display main menu and return selected options"""
    clock = pygame.time.Clock()
    animation_time = 0
    
    # Create buttons
    buttons = {
        'mode_human_ai': Button(WIDTH//2 - 150, 150, 300, 50, "Human vs AI", GREEN),
        'mode_ai_ai': Button(WIDTH//2 - 150, 220, 300, 50, "AI vs AI", PURPLE),
        
        'diff_easy': Button(WIDTH//2 - 200, 320, 120, 40, "Easy", BLUE),
        'diff_medium': Button(WIDTH//2 - 40, 320, 120, 40, "Medium", ORANGE),
        'diff_hard': Button(WIDTH//2 + 120, 320, 120, 40, "Hard", RED),
        
        'color_red': Button(WIDTH//2 - 100, 400, 80, 40, "Red", RED),
        'color_blue': Button(WIDTH//2 + 20, 400, 80, 40, "Blue", BLUE),
        
        'start_game': Button(WIDTH//2 - 100, 480, 200, 60, "START GAME", GOLD, text_color=(0,0,0), font_size=32)
    }
    
    # Set initial selections
    buttons['mode_human_ai'].selected = True
    buttons['diff_medium'].selected = True
    buttons['color_red'].selected = True
    
    selected_mode = GameMode.HUMAN_VS_AI
    selected_difficulty = Difficulty.MEDIUM
    selected_color = colors.RED
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        animation_time += dt
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in buttons.values():
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Game mode selection
                if buttons['mode_human_ai'].is_clicked(event.pos):
                    selected_mode = GameMode.HUMAN_VS_AI
                    buttons['mode_human_ai'].selected = True
                    buttons['mode_ai_ai'].selected = False
                elif buttons['mode_ai_ai'].is_clicked(event.pos):
                    selected_mode = GameMode.AI_VS_AI
                    buttons['mode_human_ai'].selected = False
                    buttons['mode_ai_ai'].selected = True
                
                # Difficulty selection
                elif buttons['diff_easy'].is_clicked(event.pos):
                    selected_difficulty = Difficulty.EASY
                    buttons['diff_easy'].selected = True
                    buttons['diff_medium'].selected = False
                    buttons['diff_hard'].selected = False
                elif buttons['diff_medium'].is_clicked(event.pos):
                    selected_difficulty = Difficulty.MEDIUM
                    buttons['diff_easy'].selected = False
                    buttons['diff_medium'].selected = True
                    buttons['diff_hard'].selected = False
                elif buttons['diff_hard'].is_clicked(event.pos):
                    selected_difficulty = Difficulty.HARD
                    buttons['diff_easy'].selected = False
                    buttons['diff_medium'].selected = False
                    buttons['diff_hard'].selected = True
                
                # Color selection (only for Human vs AI)
                elif buttons['color_red'].is_clicked(event.pos) and selected_mode == GameMode.HUMAN_VS_AI:
                    selected_color = colors.RED
                    buttons['color_red'].selected = True
                    buttons['color_blue'].selected = False
                elif buttons['color_blue'].is_clicked(event.pos) and selected_mode == GameMode.HUMAN_VS_AI:
                    selected_color = colors.BLUE
                    buttons['color_red'].selected = False
                    buttons['color_blue'].selected = True
                
                # Start game
                elif buttons['start_game'].is_clicked(event.pos):
                    game_state.game_mode = selected_mode
                    game_state.difficulty = selected_difficulty
                    game_state.human_color = selected_color
                    game_state.ai_color = colors.BLUE if selected_color == colors.RED else colors.RED
                    return
        
        # Draw menu
        screen.fill(DARK_BG)
        
        # Title with animation
        font_title = pygame.font.Font(None, 64)
        title_color = tuple(int(128 + 127 * math.sin(animation_time * 2 + i/3)) for i in range(3))
        title = font_title.render("Chain Reaction", True, title_color)
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        screen.blit(title, title_rect)
        
        # Section labels
        font_label = pygame.font.Font(None, 28)
        
        mode_label = font_label.render("Game Mode:", True, WHITE)
        screen.blit(mode_label, (WIDTH//2 - 150, 120))
        
        diff_label = font_label.render("Difficulty:", True, WHITE)
        screen.blit(diff_label, (WIDTH//2 - 150, 290))
        
        if selected_mode == GameMode.HUMAN_VS_AI:
            color_label = font_label.render("Your Color:", True, WHITE)
            screen.blit(color_label, (WIDTH//2 - 150, 370))
        
        # Draw buttons
        for key, button in buttons.items():
            # Disable color selection for AI vs AI
            if key.startswith('color_') and selected_mode == GameMode.AI_VS_AI:
                button.color = (50, 50, 50)
                button.text_color = (100, 100, 100)
            else:
                # Reset colors
                if key == 'color_red':
                    button.color = RED
                    button.text_color = WHITE
                elif key == 'color_blue':
                    button.color = BLUE
                    button.text_color = WHITE
            
            button.draw(screen)
        
        pygame.display.flip()

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
    y_offset += 40
    
    # Game mode and difficulty
    mode_text = font_small.render(f"Mode: {game_state.game_mode}", True, GRAY)
    screen.blit(mode_text, (GAME_WIDTH + 10, y_offset))
    y_offset += 20
    
    diff_text = font_small.render(f"Difficulty: {game_state.difficulty['name']}", True, GRAY)
    screen.blit(diff_text, (GAME_WIDTH + 10, y_offset))
    y_offset += 30
    
    # Current player indicator
    player_color = RED if current_player == colors.RED else BLUE
    
    if game_state.game_mode == GameMode.HUMAN_VS_AI:
        if current_player == game_state.human_color:
            player_name = "Your Turn"
        else:
            player_name = "AI Turn"
    else:  # AI vs AI
        player_name = f"AI {'Red' if current_player == colors.RED else 'Blue'}"
    
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
    y_offset = HEIGHT - 120
    if game_state.game_mode == GameMode.HUMAN_VS_AI:
        instructions = [
            "Click to place orb",
            "Chain reactions win!",
            f"You are {'Red' if game_state.human_color == colors.RED else 'Blue'}"
        ]
    else:
        instructions = [
            "AI vs AI Mode",
            "Watch the battle!",
            "Press ESC for menu"
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
    continue_text = font_small.render("Press SPACE to return to menu or ESC to exit", True, GRAY)
    continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    screen.blit(continue_text, continue_rect)
    
    pygame.display.flip()
    
    # Wait for user input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return  # Return to menu

def get_cell_from_mouse(pos):
    x, y = pos
    if x >= GAME_WIDTH:  # Click in sidebar
        return None
    return y // CELL_HEIGHT, x // CELL_WIDTH

# === AI Functions ===

def get_best_ai_move(board, ai_player, current_player, depth):
    """AI move selection using original minmax function"""
    moves = valid_moves(board, ai_player)
    if not moves:
        return None
    
    # Initialize best_value based on player
    if ai_player == colors.RED:
        best_value = -int(1e9)  # Red wants to maximize
    else:
        best_value = int(1e9)    # Blue wants to minimize
    
    best_move = None
    
    for move in moves:
        undo_info = make_move_with_undo_information(board, move, ai_player)
        value = minmax(board, depth, -int(1e9), int(1e9), current_player)
        undo_move(board, undo_info)
        
        # Different comparison based on player
        if ai_player == colors.RED:
            if value > best_value:  # Red wants higher values
                best_value = value
                best_move = move
        else:
            if value < best_value:  # Blue wants lower values
                best_value = value
                best_move = move
    
    return best_move

# === Main Game Loop ===

def run_game():
    """Main game loop"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chain Reaction - Enhanced Edition")
    clock = pygame.time.Clock()

    board = Board.Board()
    current_player = colors.RED  # Always start with RED
    
    # Reset game state
    game_state.human_start_time = time.time() if game_state.game_mode == GameMode.HUMAN_VS_AI and game_state.human_color == colors.RED else None
    game_state.human_think_time = 0
    game_state.ai_think_time = 0
    game_state.move_count = 0
    game_state.game_start_time = time.time()
    game_state.ai_thinking = False
    
    ai_move_timer = 0
    first_move_done = False  # Flag to track if first move was made

    # Handle case where AI is first player (Red) - BEFORE main game loop
    if game_state.game_mode == GameMode.HUMAN_VS_AI and game_state.human_color == colors.BLUE and not first_move_done:
        game_state.ai_thinking = True
        # Show initial board with AI thinking
        screen.fill(DARK_BG)
        draw_board(screen, board)
        draw_sidebar(screen, board, current_player)
        pygame.display.flip()
        
        # AI makes first move
        start_time = time.time()
        best_move = get_best_ai_move(board, current_player, current_player, game_state.difficulty['depth'])
        game_state.ai_think_time = time.time() - start_time
        game_state.ai_thinking = False

        if best_move:
            logged = [[False for _ in range(6)] for _ in range(9)]
            memory = [[]]
            board.make_move(current_player, best_move[0], best_move[1], logged, memory)
            game_state.move_count += 1
            save_board_to_file(board, "AI First Move:")
            
            # Update screen after AI move
            screen.fill(DARK_BG)
            draw_board(screen, board)
            draw_sidebar(screen, board, current_player)
            pygame.display.flip()
            
            if is_terminal(board):
                result = who_won(board)
                winner = "You Win!" if result < 0 else "AI Wins!" if result > 0 else "Draw!"
                show_game_over(screen, winner)
                return
            
            # Switch to human
            current_player = game_state.human_color
            game_state.human_start_time = time.time()
            first_move_done = True  # Mark first move as done

    while True:
        dt = clock.tick(FPS) / 1000.0
        game_state.animation_time += dt
        
        # Handle mouse hover (only for human players)
        if game_state.game_mode == GameMode.HUMAN_VS_AI and current_player == game_state.human_color:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < GAME_WIDTH:
                hover_result = get_cell_from_mouse(mouse_pos)
                game_state.hover_cell = hover_result
            else:
                game_state.hover_cell = None
        else:
            game_state.hover_cell = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_board_to_file(board, "Game interrupted")
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # Return to menu

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Only handle clicks for human players
                if game_state.game_mode == GameMode.HUMAN_VS_AI and current_player == game_state.human_color:
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
                        
                        # Human move
                        logged = [[False for _ in range(6)] for _ in range(9)]
                        memory = [[]]
                        board.make_move(current_player, row, col, logged, memory)
                        game_state.move_count += 1
                        save_board_to_file(board, "Human Move:")
                        
                        # IMMEDIATELY update screen after human move
                        screen.fill(DARK_BG)
                        draw_board(screen, board)
                        draw_sidebar(screen, board, current_player)
                        pygame.display.flip()
                        
                        # Check for game over
                        if is_terminal(board):
                            result = who_won(board)
                            if game_state.human_color == colors.RED:
                                winner = "You Win!" if result > 0 else "AI Wins!" if result < 0 else "Draw!"
                            else:
                                winner = "You Win!" if result < 0 else "AI Wins!" if result > 0 else "Draw!"
                            show_game_over(screen, winner)
                            return
                        
                        # Switch to AI and immediately show AI thinking
                        current_player = game_state.ai_color
                        game_state.ai_thinking = True
                        
                        # Show AI thinking immediately
                        screen.fill(DARK_BG)
                        draw_board(screen, board)
                        draw_sidebar(screen, board, current_player)
                        pygame.display.flip()
                        
                        # AI makes its move
                        start_time = time.time()
                        best_move = get_best_ai_move(board, current_player, current_player, game_state.difficulty['depth'])
                        game_state.ai_think_time = time.time() - start_time
                        game_state.ai_thinking = False

                        if best_move:
                            logged = [[False for _ in range(6)] for _ in range(9)]
                            memory = [[]]
                            board.make_move(current_player, best_move[0], best_move[1], logged, memory)
                            game_state.move_count += 1
                            save_board_to_file(board, "AI Move:")
                            
                            # IMMEDIATELY update screen after AI move
                            screen.fill(DARK_BG)
                            draw_board(screen, board)
                            draw_sidebar(screen, board, current_player)
                            pygame.display.flip()
                            
                            if is_terminal(board):
                                result = who_won(board)
                                if game_state.human_color == colors.RED:
                                    winner = "You Win!" if result > 0 else "AI Wins!" if result < 0 else "Draw!"
                                else:
                                    winner = "You Win!" if result < 0 else "AI Wins!" if result > 0 else "Draw!"
                                show_game_over(screen, winner)
                                return
                            
                            # Switch back to human
                            current_player = game_state.human_color
                            game_state.human_start_time = time.time()
        
        # AI vs AI Move Logic
        if game_state.game_mode == GameMode.AI_VS_AI:
            ai_move_timer += dt
            if ai_move_timer < game_state.ai_vs_ai_delay and not game_state.ai_thinking:
                # Still waiting for AI delay
                pass
            else:
                ai_move_timer = 0
                if not game_state.ai_thinking:
                    game_state.ai_thinking = True
                    
                    # Show AI thinking immediately
                    screen.fill(DARK_BG)
                    draw_board(screen, board)
                    draw_sidebar(screen, board, current_player)
                    pygame.display.flip()
                    
                    start_time = time.time()
                    best_move = get_best_ai_move(board, current_player, current_player, game_state.difficulty['depth'])
                    game_state.ai_think_time = time.time() - start_time
                    game_state.ai_thinking = False

                    if best_move:
                        logged = [[False for _ in range(6)] for _ in range(9)]
                        memory = [[]]
                        board.make_move(current_player, best_move[0], best_move[1], logged, memory)
                        game_state.move_count += 1
                        save_board_to_file(board, f"AI Move ({'Red' if current_player == colors.RED else 'Blue'}):")
                        
                        # IMMEDIATELY update screen after AI move
                        screen.fill(DARK_BG)
                        draw_board(screen, board)
                        draw_sidebar(screen, board, current_player)
                        pygame.display.flip()
                        
                        if is_terminal(board):
                            result = who_won(board)
                            winner = "Red AI Wins!" if result > 0 else "Blue AI Wins!" if result < 0 else "Draw!"
                            show_game_over(screen, winner)
                            return
                        
                        # Switch player
                        current_player = colors.BLUE if current_player == colors.RED else colors.RED

        # Draw everything
        screen.fill(DARK_BG)
        draw_board(screen, board)
        draw_sidebar(screen, board, current_player)
        pygame.display.flip()

def main():
    """Main function with menu loop"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chain Reaction - Enhanced Edition")
    
    while True:
        show_main_menu(screen)
        run_game()

if __name__ == "__main__":
    main()