import cell
def get_critical_mass(row, col):
    if (row in [0, 8]) and (col in [0, 5]):
        return 2  # corner
    elif (row in [0, 8]) or (col in [0, 5]):
        return 3  # edge
    else:
        return 4  # inner cell

class Board:
    def __init__(self):
         self.grid = [[cell.Cell() for _ in range(6)] for _ in range (9)]

    def make_move(self,player,row,col,logged:list[list[int]],memory:list[list[int]]): 
         if(logged[row][col]==False):
              logged[row][col] = True
              memory.append([row,col,self.grid[row][col].color,self.grid[row][col].count]) 
         self.grid[row][col].set_color(player)
         self.grid[row][col].count += 1
         if(self.grid[row][col].count>=get_critical_mass(row,col)):
              self.explode(player,row,col,logged,memory)
    
    def explode(self,player,row,col,logged,memory):
          neighbourRows = []
          neighbourColumns = []
          if(row-1>=0): neighbourRows.append(row-1)
          if(row+1<9): neighbourRows.append(row+1)
          if(col-1>=0): neighbourColumns.append(col-1)
          if(col+1<6): neighbourColumns.append(col+1)
          self.grid[row][col].color = 0
          self.grid[row][col].count = 0
          for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
               nx, ny = row + dx, col + dy
               if 0 <= nx < 9 and 0 <= ny < 6:
                    self.make_move(player, nx, ny, logged, memory)

          # for roww in neighbourRows:
          #      self.make_move(player,roww,col,logged,memory)
          # for coll in neighbourColumns:
          #      self.make_move(player,row,coll,logged,memory)
               


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
    def __str__(self):
          color_map = {1: "R", 2: "B"}
          board_str = ""
          for i in range(9):
               for j in range(6):
                    cell = self.grid[i][j]
                    if cell.count > 0:
                         color_char = color_map.get(cell.color, "?")
                         board_str += f"{cell.count}{color_char} "
                    else:
                         board_str += "0 "
               board_str += "\n"
          return board_str.strip()

              


