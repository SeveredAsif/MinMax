import copy
import Board
import colors

def custom_copy(state:Board.Board):
    b = Board.Board()
    for i in range(9):
        for j in range(6):
            b.grid[i][j].color = state.grid[i][j].color
            b.grid[i][j].count = state.grid[i][j].color
    return b 
def make_move_with_undo_information(state:Board.Board,valid_moves:list[int],maximizing_player):
    logged = [[False for _ in range(6)] for _ in range(9)]
    undo_info = []
    i,j = valid_moves
    state.make_move(maximizing_player,i,j,logged,undo_info)
    return undo_info


def undo_move(state:Board.Board,undo_info:list[list[int]]):
    for info in undo_info:
        i,j,color,count = info 
        state.grid[i][j].color = color
        state.grid[i][j].count = count
    
def result_board(state:Board.Board,valid_moves:list[int],maximizing_player):
    deep_copied_board = custom_copy(state)
    i,j = valid_moves
    deep_copied_board.make_move(maximizing_player,i,j)
    #deep_copied_board.print_board()
    #print()
    #print()
    return deep_copied_board

def heuristic(state:Board.Board,player):
    count = 0
    for row in state.grid:
        for cell in row:
            if(cell.color==colors.RED):
                count += 1
            elif(cell.color==colors.BLUE):
                count -= 1
    #print(f"heuristic: {count}")
    if (player==colors.RED):
        return count
    
    return -count 

def valid_moves(state:Board.Board,player):
    valid_moves = []
    for r in range(9):
        for c in range(6):
            cell = state.grid[r][c]
            if cell.color == player or cell.color == 0:
                valid_moves.append((r, c))
    #print(f"valid moves:{valid_moves}")
    return valid_moves

#3:36 pm - 3:54 pm  
def who_won(state:Board.Board)->int:
    #print("reaching base case!")
    has_Red = False
    has_Blue = False
    for rows in state.grid:
        for cell in rows:
            if(cell.color==colors.RED):
                has_Red = True
            elif(cell.color==colors.BLUE):
                has_Blue=True
            if(has_Red==True and has_Blue==True):
                #board filled but no one dominant color
                #print("draw!")
                return 0
    if(has_Red==True):
        #red won, +INF
        #print("red won!")
        return int(1e9)
    #blue won, -INF
    elif has_Blue:
        #print("blue won!")
        return -int(1e9)
    #print("draw!")
    return 0


#3:03 pm-3:35pm 
def is_terminal(state:Board.Board)->bool:
    red_count = 0
    blue_count = 0
    for rows in state.grid:
        for cell in rows:
            if(cell.color==colors.BLUE):
                blue_count += cell.count
            elif(cell.color==colors.RED):
                red_count += cell.count

    return (red_count == 0 and blue_count > 1) or (blue_count == 0 and red_count > 1)