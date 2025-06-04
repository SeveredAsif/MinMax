import Board
import colors
import copy

def result_board(state:Board.Board,valid_moves:list[int],maximizing_player):
    deep_copied_board = copy.deepcopy(state)
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
    color = 0
    count = 0
    #check if every cell is filled up
    # for i in range(9):
    #     for j in range(6):
    #         if(state.grid[i][j].color==0):
    #             break
    #         else: count +=1
    # if(count==54): return True 
    for i in range(9):
        for j in range(6):
            if(state.grid[i][j].color!=0):
                count +=1
            if(state.grid[i][j].color!=0 and color==0):
                color = state.grid[i][j].color
            elif(color!=0 and state.grid[i][j].color!=color):
                return False
    return color!=0 and count>1


#state is board, depth=custom by user ig, maximizing_player = true or false
def minmax(state, depth, maximizing_player):
    #print(f"depth: {depth}, player: {maximizing_player}")
    #is_terminal -- all colors are red, or all colors are blue. what if it is the first move and only color is red, will it be a terminal?
    if is_terminal(state):
        return who_won(state) #returns 0 if nobody won in a certain depth
    if(depth==0):
        return heuristic(state,maximizing_player)
    
    if maximizing_player==colors.RED:
        max_eval = -int(1e9)
        valid_movess = valid_moves(state,maximizing_player)
        #print(f"valid moves: {len(valid_movess)} for RED")
        for action in valid_movess:
            eval = minmax(result_board(state, action,maximizing_player), depth - 1, colors.BLUE)
            max_eval = max(max_eval, eval)
        #print(f"returning {max_eval} for RED at depth {depth}")
        return max_eval
    else:
        min_eval = int(1e9)
        valid_movess = valid_moves(state,colors.BLUE)
        #print(f"valid moves: {len(valid_movess)} for BLUE")
        for action in valid_movess:
            eval = minmax(result_board(state, action,colors.BLUE), depth - 1, colors.RED)
            min_eval = min(min_eval, eval)
        #print(f"returning {min_eval} for BLUE at depth {depth}")
        return min_eval