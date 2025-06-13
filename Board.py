import cell
import colors



class Board:
    def __init__(self):
         self.grid = [[cell.Cell() for _ in range(6)] for _ in range (9)]
     #     self.color_array = [0,0]
         self.game_start = True
    def get_critical_mass(self, row, col):
     if (row in [0, 8]) and (col in [0, 5]):
          return 2  # corner
     elif (row in [0, 8]) or (col in [0, 5]):
          return 3  # edge
     else:
          return 4  # inner cell
    def is_terminal(self)->bool:
     red_count = 0
     blue_count = 0
     for rows in self.grid:
          for cell in rows:
               if(cell.color==colors.BLUE):
                    blue_count += cell.count
               elif(cell.color==colors.RED):
                    red_count += cell.count

     return (red_count == 0 and blue_count > 1) or (blue_count == 0 and red_count > 1)

    def make_move(self,player,row,col,logged:list[list[int]],memory:list[list[int]]): 
     #     if explosion[row][col]:         
     #      return
         if(logged[row][col]==False):
              logged[row][col] = True
              memory.append([row,col,self.grid[row][col].color,self.grid[row][col].count]) 

     #     old_color = self.grid[row][col].color
     #     old_count = self.grid[row][col].count

     #     # Only subtract if the cell had a color
     #     if old_color != 0:
     #      self.color_array[old_color - 1] -= old_count
          # if(self.color_array[old_color - 1]<0):
          #      print(f"I found negative in make move!")


         self.grid[row][col].count += 1
         self.grid[row][col].set_color(player)
         #self.color_array[player - 1] += self.grid[row][col].count


         #self.color_array[self.grid[row][col].color-1] += self.grid[row][col].count
         if(self.grid[row][col].count>=self.get_critical_mass(row,col) ): #and explosion[row][col]==False
          #     explosion[row][col]=True
          #     self.grid[row][col].count = 0
          #     self.grid[row][col].color = 0
              #print(f"red:{self.color_array[0]},blue:{self.color_array[1]}")
              
              self.explode(player,row,col,logged,memory)
              
    
    def explode(self,player,row,col,logged,memory):
          if(self.is_terminal()):
               return 
          # old_color = self.grid[row][col].color
          # old_count = self.grid[row][col].count
          # if old_color != 0:
          #      self.color_array[old_color - 1] -= old_count
               # if(self.color_array[old_color - 1]<0):
               #      print(f"I found negative in explosion!")

          self.grid[row][col].color = 0
          self.grid[row][col].count = 0
          #if(self.color_array[0]<=0 or self.color_array[1]<=0): return 
          for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
               nx, ny = row + dx, col + dy
               if 0 <= nx < 9 and 0 <= ny < 6:
                    self.make_move(player, nx, ny, logged, memory)
          # #count = [[0 for _ in range(6)] for _ in range(9)]
          # queue = [(row,col)]
          # MAX_QUEUE_SIZE = 100
          # while queue:
          #      if len(queue) > MAX_QUEUE_SIZE:
          #           raise Exception("Explosion chain too long - possible infinite loop")
          #      i,j = queue.pop(0)
          #      # count[i][j]+=1
          #      # print(f"{i},{j} for {count[i][j]} th time")
          #      explosion[i][j] = False

          #      for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
          #           nx, ny = i + dx, j + dy
          #           if 0 <= nx < 9 and 0 <= ny < 6:
          #                if(logged[nx][ny]==False):
          #                     logged[nx][ny] = True
          #                     memory.append([nx,ny,self.grid[nx][ny].color,self.grid[nx][ny].count])

          #                self.grid[nx][ny].set_color(player)
          #                self.grid[nx][ny].count += 1 

          #                if self.grid[nx][ny].count >= get_critical_mass(nx, ny) and not explosion[nx][ny]:
          #                     explosion[nx][ny] = True
          #                     self.grid[nx][ny].count = 0
          #                     self.grid[nx][ny].color = 0
               
          #                     queue.append((nx, ny))
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
    



              


