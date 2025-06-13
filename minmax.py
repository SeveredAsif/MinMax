
import colors

from utils import *

#state is board, depth=custom by user ig, maximizing_player = true or false
def minmax(state, depth,alpha,beta ,maximizing_player):
    #print(f"depth: {depth}, player: {maximizing_player}")
    #is_terminal -- all colors are red, or all colors are blue. what if it is the first move and only color is red, will it be a terminal?
    if state.is_terminal():
        return who_won(state) #returns 0 if nobody won in a certain depth
    if(depth==0):
        return heuristic_chain_reaction_opportunity(state,maximizing_player)
    
    if maximizing_player==colors.RED:
        max_eval = -int(1e9)
        valid_movess = valid_moves(state,maximizing_player)
        #print(f"valid moves: {len(valid_movess)} for RED")
        for action in valid_movess:
            undo_info = make_move_with_undo_information(state,action,maximizing_player)
            eval = minmax(state, depth - 1, alpha,beta ,colors.BLUE)
            undo_move(state,undo_info)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        #print(f"returning {max_eval} for RED at depth {depth}")
        return max_eval
    else:
        min_eval = int(1e9)
        valid_movess = valid_moves(state,colors.BLUE)
        #print(f"valid moves: {len(valid_movess)} for BLUE")
        for action in valid_movess:
            undo_info = make_move_with_undo_information(state,action,colors.BLUE)
            eval = minmax(state, depth - 1, alpha,beta ,colors.RED)
            undo_move(state,undo_info)
            #eval = minmax(result_board(state, action,colors.BLUE), depth - 1, alpha,beta,colors.RED)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        #print(f"returning {min_eval} for BLUE at depth {depth}")
        return min_eval