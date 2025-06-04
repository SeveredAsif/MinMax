import Board
#state is board, depth=custom by user ig, maximizing_player = true or false
def minmax(state, depth, maximizing_player):
    #is_terminal -- all colors are red, or all colors are blue. what if it is the first move and only color is red, will it be a terminal?
    if is_terminal(state) or depth == 0:
        return state
    
    if maximizing_player:
        max_eval = -infinity
        for action in actions(state):
            eval = minmax(result(state, action), depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = infinity
        for action in actions(state):
            eval = minmax(result(state, action), depth - 1, True)
            min_eval = min(min_eval, eval)
        return min_eval