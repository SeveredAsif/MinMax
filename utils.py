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
        # state.color_array[0] = red_count
        # state.color_array[1] = blue_count
        #print(f"red:{state.color_array[0]},blue:{state.color_array[1]}")
    
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
    # if (player==colors.RED):
    #     return count
    
    return count 

def heuristic_orb_count_diff(state:Board.Board,player):
    score = 0
    for row in state.grid:
        for cell in row:
            if cell.color == player:
                score += cell.count
            elif cell.color != 0:
                score -= cell.count
    if (player==colors.RED):
        return score
    
    return -score 

def heuristic_edge_corner_control(state:Board.Board,player):
    score = 0
    for i in range(9):
        for j in range(6):
            cell = state.grid[i][j]
            if cell.color == player:
                if (i in [0, 8]) and (j in [0, 5]):
                    score += 3  # corner
                elif i in [0, 8] or j in [0, 5]:
                    score += 2  # edge
                else:
                    score += 1  # center
    
    if (player==colors.RED):
        return score    
    return -score

def heuristic_vulnerability(state:Board.Board, player):

    score = 0
    for i in range(9):
        for j in range(6):
            cell = state.grid[i][j]
            if cell.color == player:
                critical = state.get_critical_mass(i, j)
                
                if cell.count == critical - 1:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < 9 and 0 <= nj < 6:
                            neighbor = state.grid[ni][nj]
                            if neighbor.color != 0 and neighbor.color != player:
                                score -= 5  
                
                else:
                    safe = True
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < 9 and 0 <= nj < 6:
                            neighbor = state.grid[ni][nj]
                            if neighbor.color != 0 and neighbor.color != player:
                                safe = False
                                break
                    if safe:
                        score += 2  # Reward for each safe orb
    if player == colors.RED:
        return score
    return -score

def heuristic_chain_reaction_opportunity(state:Board.Board,player):
    reward = 0
    for i in range(9):
        for j in range(6):
            cell = state.grid[i][j]
            if cell.color == player:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < 9 and 0 <= nj < 6:
                        neighbor = state.grid[ni][nj]
                        if neighbor.color != 0 and neighbor.color == player:
                            if neighbor.count == state.get_critical_mass(ni, nj) - 1:
                                reward += 5
                            elif neighbor.count == state.get_critical_mass(ni, nj) - 2:
                                reward += 3

                
    if (player==colors.RED):
        return reward
    
    return -reward 


def combined_heuristic(state: Board.Board, player):
    orb_score = heuristic_orb_count_diff(state, player)
    chain_score = heuristic_chain_reaction_opportunity(state, player)
    
    
    final_score = (
        1.0 * orb_score +       
        0.7 * chain_score       
    )

    return final_score




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
                 print("draw!")
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
# def is_terminal(state:Board.Board)->bool:
#     red_count = 0
#     blue_count = 0
#     for rows in state.grid:
#         for cell in rows:
#             if(cell.color==colors.BLUE):
#                 blue_count += cell.count
#             elif(cell.color==colors.RED):
#                 red_count += cell.count

#     return (red_count == 0 and blue_count > 1) or (blue_count == 0 and red_count > 1)