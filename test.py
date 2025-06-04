import unittest
from unittest.mock import patch
import Board
import colors
from minmax import (result_board, heuristic, valid_moves, 
                   who_won, is_terminal, minmax)

class TestGameFunctions(unittest.TestCase):
    
    def setUp(self):
        """Initialize a fresh board before each test"""
        self.board = Board.Board()
        
    def test_result_board(self):
        """Test that making a move creates a new board with the correct change"""
        # Make initial move on a copy
        new_board = result_board(self.board, (0, 0), colors.RED)
        
        # Original board should remain unchanged
        self.assertEqual(self.board.grid[0][0].color, 0)
        # New board should have the move
        self.assertEqual(new_board.grid[0][0].color, colors.RED)
        
    def test_heuristic(self):
        """Test the heuristic evaluation function"""
        # Empty board should have 0 heuristic
        self.assertEqual(heuristic(self.board, colors.RED), 0)
        
        # Make some moves
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        
        # Test heuristic for both players
        self.assertEqual(heuristic(self.board, colors.RED), 0)  # 1 red - 1 blue = 0
        self.assertEqual(heuristic(self.board, colors.BLUE), 0)  # -(1 red - 1 blue) = 0
        
    def test_valid_moves(self):
        """Test that valid moves are correctly identified"""
        # Initial state - all empty cells should be valid
        moves = valid_moves(self.board, colors.RED)
        self.assertEqual(len(moves), 54)  # 9x6 grid
        
        # After some moves
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        
        # RED can move to any empty cell or red cell
        moves = valid_moves(self.board, colors.RED)
        self.assertEqual(len(moves), 53)  # one less because (1,1) is blue
        
        # BLUE can move to any empty cell or blue cell
        moves = valid_moves(self.board, colors.BLUE)
        self.assertEqual(len(moves), 53)  # one less because (0,0) is red
        
    def test_who_won(self):
        """Test the terminal state detection"""
        # Empty board - no winner
        self.assertEqual(who_won(self.board), 0)
        
        # All red board
        for r in range(9):
            for c in range(6):
                self.board.make_move(colors.RED, r, c)
        self.assertEqual(who_won(self.board), int(1e9))
        
        # All blue board
        self.board = Board.Board()
        for r in range(9):
            for c in range(6):
                self.board.make_move(colors.BLUE, r, c)
        self.assertEqual(who_won(self.board), -int(1e9))
        
        # Mixed board
        self.board = Board.Board()
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        self.assertEqual(who_won(self.board), 0)
        
    def test_is_terminal(self):
        """Test if terminal state is correctly identified"""
        # Empty board is not terminal
        self.assertFalse(is_terminal(self.board))
        
        # Board with mixed colors is not terminal
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        self.assertFalse(is_terminal(self.board))
        
        # All red board is terminal
        for r in range(9):
            for c in range(6):
                self.board.make_move(colors.RED, r, c)
        self.assertTrue(is_terminal(self.board))
        
        # All blue board is terminal
        self.board = Board.Board()
        for r in range(9):
            for c in range(6):
                self.board.make_move(colors.BLUE, r, c)
        self.assertTrue(is_terminal(self.board))
        
    def test_minimax_terminal_state(self):
        """Test minimax with terminal state (RED wins)"""
        # Create a winning board for RED
        for r in range(9):
            for c in range(6):
                self.board.make_move(colors.RED, r, c)
                
        result = minmax(self.board, 3, colors.RED)
        self.assertEqual(result, int(1e9))
        
    def test_minimax_depth_zero(self):
        """Test minimax with depth 0 (should return heuristic)"""
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        
        # Mock heuristic to return known value
        with patch('minmax.heuristic', return_value=42):
            result = minmax(self.board, 0, colors.RED)
            self.assertEqual(result, 42)
            
    def test_minimax_maximizing_player(self):
        """Test minimax with maximizing player (RED)"""
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        
        # Mock valid moves and heuristic returns
        with patch('minmax.valid_moves', return_value=[(2,2), (3,3)]):
            with patch('minmax.heuristic', side_effect=[10, -5]):
                result = minmax(self.board, 1, colors.RED)
                self.assertEqual(result, 10)  # Should choose max of [10, -5]
                
    def test_minimax_minimizing_player(self):
        """Test minimax with minimizing player (BLUE)"""
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 1, 1)
        
        # Mock valid moves and heuristic returns
        with patch('minmax.valid_moves', return_value=[(2,2), (3,3)]):
            with patch('minmax.heuristic', side_effect=[10, -5]):
                result = minmax(self.board, 1, colors.BLUE)
                self.assertEqual(result, -5)  # Should choose min of [10, -5]
                
    def test_minimax_integration(self):
        """Integration test with actual moves and small depth"""
        # Make initial moves to create a simple scenario
        self.board.make_move(colors.RED, 0, 0)
        self.board.make_move(colors.BLUE, 0, 1)
        
        # Run minimax with depth 2
        result = minmax(self.board, 2, colors.RED)
        
        # We can't predict exact value but should be within reasonable bounds
        self.assertTrue(abs(result) < int(1e9))

if __name__ == '__main__':
    unittest.main()
# import colors
# from Board import Board
# from minmax import minmax, valid_moves, result_board,is_terminal  # adjust import as needed

# def test_minimax_play():
#     board = Board()
#     current_player = colors.RED
#     depth = 2  # low depth for fast testing

#     turn = 1
#     #while not is_terminal(board):
#     print(f"\n=== Turn {turn}: {'Red' if current_player == colors.RED else 'Blue'} ===")
#     #board.print_board()

#     moves = valid_moves(board, current_player)
#     #print(f"len: {len(moves)}")
#     # if not moves:
#     #     print("No valid moves.")
#     #     break

#     best_value = -int(1e9) if current_player == colors.RED else int(1e9)
#     best_move = None

#     for move in moves[0:2]:
#         simulated_board = result_board(board, move, current_player)
#         #simulated_board.print_board()

#         value = minmax(simulated_board, depth, colors.BLUE if current_player == colors.RED else colors.RED)
# #         if (current_player == colors.RED and value > best_value) or \
# #            (current_player == colors.BLUE and value < best_value):
# #             best_value = value
# #             best_move = move

# #     if best_move:
# #         print(f"{'Red' if current_player == colors.RED else 'Blue'} plays at {best_move}")
# #         board.make_move(current_player, best_move[0], best_move[1])
# #     else:
# #         print("No best move found.")
# #         break

# #     current_player = colors.BLUE if current_player == colors.RED else colors.RED
# #     turn += 1

# # print("\n=== Final Board ===")
# # board.print_board()
# # winner = board.who_won()
# # if winner == int(1e9):
# #     print("Red wins!")
# # elif winner == -int(1e9):
# #     print("Blue wins!")
# # else:
# #     print("Draw.")

# test_minimax_play()