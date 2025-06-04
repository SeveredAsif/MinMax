import colors
import Board 
from utils import *
from minmax import *

def save_board_to_file(board, filename="game_log.txt"):
    """Save current board state to file, overwriting previous content"""
    with open(filename, 'w') as f:
        f.write(str(board) + "\n")  # Assumes Board class has __str__ method
        # Or use board.print_board() if it returns a string

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
    
    # Initial board
    b.print_board()
    save_board_to_file(b, game_log)
    
    while True:
        # Human move
        if human_color == colors.BLUE:
            print("You are Blue. Make your move (row, column):")
        else:
            print("You are Red. Make your move (row, column):")
        
        try:
            row = int(input("Row: "))
            column = int(input("Column: "))
            
            while b.grid[row][column].color != 0 and b.grid[row][column].color != human_color:
                print("Invalid move. Try again!")
                row = int(input("Row: "))
                column = int(input("Column: "))
                
            b.make_move(human_color, row, column)
            b.print_board()
            save_board_to_file(b, game_log)
            print(f"Board saved to {game_log}")
            
        except (ValueError, IndexError):
            print("Invalid input! Please enter numbers within board dimensions.")
            continue
        
        # Check for terminal state after human move
        if is_terminal(b):
            print("Game over!")
            break
            
        # AI move
        print("\nAI is thinking...")
        best_value = -int(1e9) if ai_color == colors.RED else int(1e9)
        best_move = None
        moves = valid_moves(b, ai_color)
        
        for move in moves:
            simulated_board = result_board(b, move, ai_color)
            value = minmax(simulated_board, 2, -int(1e9), int(1e9), ai_color)
            
            if (ai_color == colors.RED and value > best_value) or \
               (ai_color == colors.BLUE and value < best_value):
                best_value = value
                best_move = move
        
        if best_move:
            b.make_move(ai_color, best_move[0], best_move[1])
            print(f"AI moves to {best_move}")
            print(str(b))
            save_board_to_file(b, game_log)
            print(f"Board saved to {game_log}\n")
            
            # Check for terminal state after AI move
            if is_terminal(b):
                print("Game over!")
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