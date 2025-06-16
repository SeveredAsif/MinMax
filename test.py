import time
import itertools
import Board
import colors
from minmax import *
from utils import *

class TestStats:
    def __init__(self):
        self.total_games = 0
        self.red_wins = 0
        self.blue_wins = 0
        self.draws = 0
        self.moves_sum = 0
        self.time_sum = 0
        self.heuristic_wins = {}  # {heuristic_name: wins}
        self.color_wins = {"Red": 0, "Blue": 0}
        
    def add_game_result(self, red_heur_name, blue_heur_name, winner, moves, game_time):
        self.total_games += 1
        self.moves_sum += moves
        self.time_sum += game_time
        
        # Track wins by color
        if winner > 0:  # Red wins
            self.red_wins += 1
            self.color_wins["Red"] += 1
            self.heuristic_wins[red_heur_name] = self.heuristic_wins.get(red_heur_name, 0) + 1
        elif winner < 0:  # Blue wins
            self.blue_wins += 1
            self.color_wins["Blue"] += 1
            self.heuristic_wins[blue_heur_name] = self.heuristic_wins.get(blue_heur_name, 0) + 1
        else:
            self.draws += 1
    
    def get_summary(self):
        avg_moves = self.moves_sum / self.total_games if self.total_games > 0 else 0
        avg_time = self.time_sum / self.total_games if self.total_games > 0 else 0
        
        return f"""
=== Test Statistics ===
Total Games: {self.total_games}
Red Wins: {self.red_wins} ({(self.red_wins/self.total_games)*100:.1f}%)
Blue Wins: {self.blue_wins} ({(self.blue_wins/self.total_games)*100:.1f}%)
Draws: {self.draws} ({(self.draws/self.total_games)*100:.1f}%)
Average Moves per Game: {avg_moves:.1f}
Average Time per Game: {avg_time:.2f}s

Heuristic Performance:
{self._format_heuristic_stats()}

Color Performance:
{self._format_color_stats()}
"""

    def _format_heuristic_stats(self):
        if not self.heuristic_wins:
            return "No heuristic data available"
        
        result = []
        for heur, wins in self.heuristic_wins.items():
            win_rate = (wins / self.total_games) * 100
            result.append(f"{heur}: {wins} wins ({win_rate:.1f}%)")
        return "\n".join(result)
    
    def _format_color_stats(self):
        if not self.color_wins:
            return "No color data available"
        
        result = []
        for color, wins in self.color_wins.items():
            win_rate = (wins / self.total_games) * 100
            result.append(f"{color}: {wins} wins ({win_rate:.1f}%)")
        return "\n".join(result)

def get_best_ai_move(board, ai_player, depth, f_heuristic):
    """Simplified version of get_best_ai_move for testing"""
    moves = valid_moves(board, ai_player)
    if not moves:
        return None
    
    if ai_player == colors.RED:
        best_value = -int(1e9)
    else:
        best_value = int(1e9)
    
    best_move = None
    opponent_player = colors.BLUE if ai_player == colors.RED else colors.RED
    
    for move in moves:
        undo_info = make_move_with_undo_information(board, move, ai_player)
        value = minmax(board, depth, -int(1e9), int(1e9), opponent_player, f_heuristic)
        undo_move(board, undo_info)
        
        if ai_player == colors.RED:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move
    
    return best_move if best_move else moves[0]

def play_game(red_heuristic, blue_heuristic, depth):
    """Play a single game with given heuristics and depth"""
    board = Board.Board()
    current_player = colors.RED
    moves_count = 0
    start_time = time.time()
    
    while not board.is_terminal():
        if current_player == colors.RED:
            move = get_best_ai_move(board, current_player, depth, red_heuristic)
            heuristic = red_heuristic
        else:
            move = get_best_ai_move(board, current_player, depth, blue_heuristic)
            heuristic = blue_heuristic
            
        if move:
            logged = [[False for _ in range(6)] for _ in range(9)]
            memory = [[]]
            board.make_move(current_player, move[0], move[1], logged, memory)
            moves_count += 1
            current_player = colors.BLUE if current_player == colors.RED else colors.RED
    
    game_time = time.time() - start_time
    result = who_won(board)
    return result, moves_count, game_time

def run_tests():
    # All available heuristics
    heuristics = [
            ("Simple", heuristic),
            ("Orb Diff", heuristic_orb_count_diff),
            ("Edge/Corner", heuristic_edge_corner_control),
            ("Vulnerability", heuristic_vulnerability),
            ("Chain Reaction", heuristic_chain_reaction_opportunity),
            ("Orb + Chain",combined_heuristic),
    ]
    
    # Test depths
    depths = [3]
    
    for depth in depths:
        print(f"\nTesting depth {depth}...")
        stats = TestStats()
        
        # Write depth header
        with open("test2.txt", "a") as f:
            f.write(f"\n{'='*50}\nDepth {depth} Tests\n{'='*50}\n")
        
        # Test all possible heuristic combinations
        for red_heur, blue_heur in itertools.product(heuristics, repeat=2):
            if red_heur[0] == blue_heur[0]:  # Skip same heuristic vs itself
                continue
                
            print(f"Testing Red({red_heur[0]}) vs Blue({blue_heur[0]})...")
            
            # Play the game
            result, moves, game_time = play_game(red_heur[1], blue_heur[1], depth)
            
            # Record results
            stats.add_game_result(red_heur[0], blue_heur[0], result, moves, game_time)
            
            # Write game results immediately
            with open("test2.txt", "a") as f:
                f.write(f"\nRed({red_heur[0]}) vs Blue({blue_heur[0]}):\n")
                winner = "Red" if result > 0 else "Blue" if result < 0 else "Draw"
                f.write(f"Winner: {winner}\n")
                f.write(f"Moves: {moves}\n")
                f.write(f"Time: {game_time:.2f}s\n")
                f.flush()  # Ensure it's written to disk
        
        # Write depth summary after all games at this depth
        with open("test.txt", "a") as f:
            f.write(f"\nDepth {depth} Summary:\n")
            f.write(stats.get_summary())
            f.flush()  # Ensure it's written to disk

if __name__ == "__main__":
    print("Starting AI vs AI heuristic tests...")
    run_tests()
    print("Tests completed! Check test.txt for results.")
