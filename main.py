import colors
import Board 
from utils import *
from minmax import *

def save_board_to_file(board, filename="game_log.txt"):
    """Save current board state to file, overwriting previous content"""
    with open(filename, 'w') as f:
        f.write(str(board) + "\n")


def main():
    b = Board.Board()
    game_log = "game_log.txt"

    # Player color selection
    print("Choose your color (1 for Blue, 2 for Red):")
    player_color = int(input())
    while player_color not in [1, 2]:
        print("Invalid choice. Enter 1 for Blue or 2 for Red:")
        player_color = int(input())

    human_color = colors.BLUE if player_color == 1 else colors.RED
    ai_color = colors.RED if human_color == colors.BLUE else colors.BLUE

    # AI heuristic selection
    heuristics = [
        ("Simple", heuristic),
        ("Orb Diff", heuristic_orb_count_diff),
        ("Edge/Corner", heuristic_edge_corner_control),
        ("Vulnerability", heuristic_vulnerability),
        ("Chain Reaction", heuristic_chain_reaction_opportunity),
        ("Orb + Chain", combined_heuristic),
    ]
    print("Choose AI heuristic:")
    for idx, (name, _) in enumerate(heuristics):
        print(f"{idx+1}: {name}")
    ai_heuristic_idx = int(input("Enter number: ")) - 1
    while ai_heuristic_idx < 0 or ai_heuristic_idx >= len(heuristics):
        ai_heuristic_idx = int(input("Invalid. Enter number: ")) - 1
    ai_heuristic = heuristics[ai_heuristic_idx][1]

    # AI depth selection
    print("Choose AI search depth (1-4 recommended):")
    try:
        ai_depth = int(input())
        if ai_depth < 1:
            ai_depth = 1
    except ValueError:
        ai_depth = 2

    # Initial board
    b.print_board()
    save_board_to_file(b, game_log)

    while True:
        # Human move
        print(f"You are {'Blue' if human_color == colors.BLUE else 'Red'}. Make your move (row, column):")
        try:
            row = int(input("Row: "))
            column = int(input("Column: "))
            while b.grid[row][column].color != 0 and b.grid[row][column].color != human_color:
                print("Invalid move. Try again!")
                row = int(input("Row: "))
                column = int(input("Column: "))
            logged = [[False for _ in range(6)] for _ in range(9)]
            memory = [[]]
            b.make_move(human_color, row, column, logged, memory)
            b.print_board()
            save_board_to_file(b, game_log)
            print(f"Board saved to {game_log}")
        except (ValueError, IndexError):
            print("Invalid input! Please enter numbers within board dimensions.")
            continue

        # Check for terminal state after human move
        if b.is_terminal():
            print("Game over!")
            break

        # AI move
        print("\nAI is thinking...")
        moves = valid_moves(b, ai_color)
        if not moves:
            print("AI has no valid moves. Game over!")
            break
        best_value = -int(1e9) if ai_color == colors.RED else int(1e9)
        best_move = None
        opponent = colors.BLUE if ai_color == colors.RED else colors.RED
        for move in moves:
            undo_info = make_move_with_undo_information(b, move, ai_color)
            value = minmax(b, ai_depth, -int(1e9), int(1e9), opponent, ai_heuristic)
            undo_move(b, undo_info)
            if (ai_color == colors.RED and value > best_value) or (ai_color == colors.BLUE and value < best_value):
                best_value = value
                best_move = move
        if best_move:
            logged = [[False for _ in range(6)] for _ in range(9)]
            memory = [[]]
            b.make_move(ai_color, best_move[0], best_move[1], logged, memory)
            print(f"AI moves to {best_move}")
            b.print_board()
            save_board_to_file(b, game_log)
            print(f"Board saved to {game_log}\n")
            if b.is_terminal():
                print("Game over!")
                break
        else:
            print("AI could not find a valid move. Game over!")
            break

if __name__ == "__main__":
    main()
# import colors
# import Board
# b = Board.Board()
# from utils import *
# from minmax import *

# b.print_board()

# while(1):
#     print("You are player Blue,make a move. Give row,column")
#     row = input()
#     row = int(row)
#     column = input()
#     column = int(column)
#     while(b.grid[row][column].color!=0 and b.grid[row][column].color!=colors.BLUE):
#         print(b.grid[row][column].color)
#         print("Wrong move,try again!")
#         row = input()
#         row = int(row)
#         column = input()
#         column = int(column)
#     b.make_move(colors.BLUE,row,column)
#     b.print_board()
#     print()
#     best_value = -int(1e9)
#     moves = valid_moves(b, colors.RED)
#     best_move = None

#     for move in moves:
#         simulated_board = result_board(b, move, colors.RED)
# #         #simulated_board.print_board()
#         value = minmax(simulated_board, 2,-int(1e9),int(1e9) ,colors.RED)
#         if(value>best_value):
#             best_value = value 
#             best_move = move
#             print()
            
#     b.make_move(colors.RED,best_move[0],best_move[1])
#     b.print_board()
#     print()