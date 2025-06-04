import cell
class Board:
    def __init__(self):
         self.grid = [[cell.Cell() for _ in range(6)] for _ in range (9)]

    def make_move(self,player,row,col):
         self.grid[row][col].set_color(player)
         self.grid[row][col].count += 1
     
    def print_board(self):
         color_map = {1: "R", 2: "B"}
         for i in range(9):
              for j in range(6):
                   if(self.grid[i][j].count>0):
                        color_char = color_map.get(self.grid[i][j].color)
                        print(f"{self.grid[i][j].count}{color_char}",end=" ")
                   else:
                        print("0 ",end=" ")
              print()
              
