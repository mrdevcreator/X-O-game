from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
# from math import cos,sin
# import random

class MidpointLine:
    def __init__(self):
        self.__midpoint_points = []

    def find_zone(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        if abs(dx) > abs(dy):
            if dx >= 0 and dy >= 0:
                return 0
            elif dx <= 0 and dy >= 0:
                return 3
            elif dx <= 0 and dy <= 0:
                return 4
            elif dx >= 0 and dy <= 0:
                return 7
        else:
            if dx >= 0 and dy >= 0:
                return 1
            elif dx <= 0 and dy >= 0:
                return 2
            elif dx <= 0 and dy <= 0:
                return 5
            elif dx >= 0 and dy <= 0:
                return 6

    def convert_to_zone0(self, x1, y1, zone):
        if zone == 0:
            return x1, y1
        elif zone == 1:
            return y1, x1
        elif zone == 2:
            return y1, -x1
        elif zone == 3:
            return -x1, y1
        elif zone == 4:
            return -x1, -y1
        elif zone == 5:
            return -y1, -x1
        elif zone == 6:
            return -y1, x1
        elif zone == 7:
            return x1, -y1

    def convert_to_original_zone(self, x1, y1, zone):

        if zone == 0:
            return x1, y1
        elif zone == 1:
            return y1, x1
        elif zone == 2:
            return -y1, x1
        elif zone == 3:
            return -x1, y1
        elif zone == 4:
            return -x1, -y1
        elif zone == 5:
            return -y1, -x1
        elif zone == 6:
            return y1, -x1
        elif zone == 7:
            return x1, -y1

    def midpoint(self, x1, y1, x2, y2,color):
        glBegin(GL_POINTS)
        glColor3f(*color)
            
        zone = self.find_zone(x1, y1, x2, y2)

        x1_to_z0, y1_to_z0 = self.convert_to_zone0(x1, y1, zone)
        x2_to_z0, y2_to_z0 = self.convert_to_zone0(x2, y2, zone)

        dy = y2_to_z0 - y1_to_z0
        dx = x2_to_z0 - x1_to_z0
        d = 2 * dy - dx
        d_E = 2 * dy
        d_NE = 2 * (dy - dx)

        x = x1_to_z0
        y = y1_to_z0

        original_x, original_y = self.convert_to_original_zone(x, y, zone)
        glVertex2f(original_x, original_y)

        while x <= x2_to_z0:
            self.__midpoint_points.append((original_x, original_y))

            if d < 0:
                x = x + 1
                d = d + d_E
            else:
                x = x + 1
                y = y + 1
                d = d + d_NE

            original_x, original_y = self.convert_to_original_zone(x, y, zone)
            glVertex2f(original_x, original_y)

        glEnd()

class MidpointCircle:
    def __init__(self):
        self.__radius = None
        self.__center_x = None
        self.__center_y = None
        self.__midpoint_points = []

    def set_circle_values(self, radius, center_x=0, center_y=0):
        self.__radius = radius
        self.__center_x = center_x
        self.__center_y = center_y

    def convert_to_other_zone(self, x1, y1, zone):
        if zone == 0:
            return x1, y1
        elif zone == 1:
            return y1, x1
        elif zone == 2:
            return -y1, x1
        elif zone == 3:
            return -x1, y1
        elif zone == 4:
            return -x1, -y1
        elif zone == 5:
            return -y1, -x1
        elif zone == 6:
            return y1, -x1
        elif zone == 7:
            return x1, -y1

    def midpoint_circle_algorithm(self, radius, center_x=0.0, center_y=0.0, y=0):
        glBegin(GL_POINTS)
        glColor3f(1.0,0.0,0.0)
        
        d = 1 - radius
        
        x = radius
        glVertex2f(x + center_x, y + center_y)

        for i in range(8):
            x_other, y_other = self.convert_to_other_zone(x, y, i)
            glVertex2f(x_other + center_x, y_other + center_y)

        while x > y:
            if d < 0:
                y = y + 1
                d = d + 2 * y + 3
            else:
                x = x - 1
                y = y + 1
                d = d + 2 * y - 2 * x + 5

            self.__midpoint_points.append((x, y))

            glVertex2f(x + center_x, y + center_y)

            for i in range(8):
                x_other, y_other = self.convert_to_other_zone(x, y, i)
                self.__midpoint_points.append((x_other, y_other))
                glVertex2f(x_other + center_x, y_other + center_y)

        glEnd()

    def filled_circle(self, radius, center_x=0, center_y=0):
        for i in range(radius):
            self.midpoint_circle_algorithm(radius, center_x, center_y)

class Game:
    WINDOW_WIDTH, WINDOW_HEIGHT = 500, 500

    def __init__(self):
        self.game_over = False
        self.draw = False
        self.mode = "AI"
        self.win = None
        self.paused = True
        self.rows = 3
        self.cols = 3
        self.x = 0
        self.y = 0
        self.turnCounter = 0
        self.possibleNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.gameBoard = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
    
    def evaluate_board(self, board):
        if self.checkForWinner(board) == 'X':
            return 1  
        elif self.checkForWinner(board) == 'O':
            return -1  
        elif ' ' not in [cell for row in board for cell in row]:
            return 0  
        else:
            return None  
    
    def minimax(self, board, depth,maximizing_player):
        score = self.evaluate_board(board)
        if score is not None:
            return score

        if maximizing_player:
            max_eval = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == ' ':
                        board[i][j] = 'X'
                        eval = self.minimax(board, depth + 1,False)
                        board[i][j] = ' '  
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == ' ':
                        board[i][j] = 'O'
                        eval = self.minimax(board, depth + 1,True)
                        board[i][j] = ' '  
                        min_eval = min(min_eval, eval)
            return min_eval
        
    def find_best_move(self):
        best_val = float('-inf')
        best_move = None
        for i in range(3):
            for j in range(3):
                if self.gameBoard[i][j] == ' ':
                    self.gameBoard[i][j] = 'X'
                    move_val = self.minimax(self.gameBoard, 0,False)
                    self.gameBoard[i][j] = ' '  

                    if move_val > best_val:
                        best_move = (i, j)
                        best_val = move_val

        return best_move
    
    def draw_xx(self, midpoint_line):
        color = [1.0, 0.0, 0.0]

        x1, y1 = self.WINDOW_WIDTH - 35, self.WINDOW_HEIGHT - 35
        x2, y2 = self.WINDOW_WIDTH - 8, self.WINDOW_HEIGHT - 8
        midpoint_line.midpoint(x1, y1, x2, y2, color)

        x3, y3 = self.WINDOW_WIDTH - 35, self.WINDOW_HEIGHT - 8
        x4, y4 = self.WINDOW_WIDTH - 8, self.WINDOW_HEIGHT - 35
        midpoint_line.midpoint(x3, y3, x4, y4, color)
    def draw_arrow(self, midpoint_line):
        color = [0.0, 1.0, 0.0]
        x1, y1 = self.WINDOW_WIDTH - (self.WINDOW_WIDTH - 25), self.WINDOW_HEIGHT - 9
        x2, y2 = self.WINDOW_WIDTH - (self.WINDOW_WIDTH - 25), self.WINDOW_HEIGHT - 35

        x3, y3 = self.WINDOW_WIDTH - (self.WINDOW_WIDTH - 8), self.WINDOW_HEIGHT - 22
        midpoint_line.midpoint(x1, y1, x3, y3, color)
        midpoint_line.midpoint(x3 - 0.2, y3 - 0.2, x2, y2, color)
        midpoint_line.midpoint(x3, y3, x2 + 20, y3, color)
    def draw_button(self, midpoint_line, is_play):
        color = [0.9, 0.5, 0.3]

        if not is_play:
            x1, y1 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) - 6), self.WINDOW_HEIGHT - 8
            x2, y2 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) - 6), self.WINDOW_HEIGHT - 35
            midpoint_line.midpoint(x1, y1, x2, y2, color)

            x3, y3 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) + 6), self.WINDOW_HEIGHT - 8
            x4, y4 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) + 6), self.WINDOW_HEIGHT - 36
            midpoint_line.midpoint(x3, y3, x4, y4, color)
        else:
            x1, y1 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) + 15), self.WINDOW_HEIGHT - 8
            x2, y2 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) + 15), self.WINDOW_HEIGHT - 36
            midpoint_line.midpoint(x1, y1, x2, y2, color)

            x3, y3 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) - 15), self.WINDOW_HEIGHT - 22
            midpoint_line.midpoint(x1, y1, x3, y3, color)
            midpoint_line.midpoint(x3, y3, x2 - 0.5, y2 - 0.5, color)
        if is_play and not self.game_over:
            option_button_color = [0.3, 0.5, 0.9]
            option_button_text = "AI" if (self.mode=="AI") else "Player 2"

            option_x1, option_y1 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) - 40), self.WINDOW_HEIGHT - 8
            option_x2, option_y2 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) - 40), self.WINDOW_HEIGHT - 35

            midpoint_line.midpoint(option_x1, option_y1, option_x2, option_y2, option_button_color)

            option_x3, option_y3 = self.WINDOW_WIDTH - ((self.WINDOW_WIDTH // 2) - 60), self.WINDOW_HEIGHT - 22
            midpoint_line.midpoint(option_x1, option_y1, option_x3, option_y3, option_button_color)
            midpoint_line.midpoint(option_x3, option_y3, option_x2 - 0.5, option_y2 - 0.5, option_button_color)

            glColor3f(1.0, 1.0, 1.0)
            glRasterPos2i(option_x3 + 5, option_y3 - 5)
            for character in option_button_text:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(character))

    def is_point(self,x, y,button_type):
        if button_type == "x":
            x2,y2 = 479,23
        elif button_type == "||":
            x2,y2 = 249,23
        elif button_type == "<>":
            x2,y2 = 296,23
        else:
            x2,y2 = 25,23

        if ((x-x2)**2)+((y-y2)**2) <= (22**2):
          return True
        else:
          return False

    def draw_game_over_text(self):
        new_sc = self.win
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2i(185, 435)
        for character in new_sc:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(character))

    def is_point_inside(self, x=0, y=0, n=0):
        if ((x-150)**2)+((y-150)**2) <= (48**2) or n==1:
          return (150,350,1)
        if ((x-250)**2)+((y-150)**2) <= (48**2) or n==2:
          return (250,350,2)
        if ((x-350)**2)+((y-150)**2) <= (48**2) or n==3:
          return (350,350,3)
        if ((x-150)**2)+((y-250)**2) <= (48**2) or n==4:
          return (150,250,4)
        if ((x-250)**2)+((y-250)**2) <= (48**2) or n==5:
          return (250,250,5)
        if ((x-350)**2)+((y-250)**2) <= (48**2) or n==6:
          return (350,250,6)
        if ((x-150)**2)+((y-350)**2) <= (48**2) or n==7:
          return (150,150,7)
        if ((x-250)**2)+((y-350)**2) <= (48**2) or n==8:
          return (250,150,8)
        if ((x-350)**2)+((y-350)**2) <= (48**2) or n==9:
          return (350,150,9)

    def modifyArray(self, num, turn):
        num -= 1
        row = num // 3
        col = num % 3
        if self.gameBoard[row][col] == ' ':
            self.gameBoard[row][col] = turn
        else:
            print("Invalid move. Please try again.")

    def draw_board(self, midpoint_line):
        x1, y1 = (200, 100)
        x2, y2 = (200, 400)
        midpoint_line.midpoint(x1, y1, x2, y2, (1.0, 1.0, 1.0))
        midpoint_line.midpoint(300, y1, 300, y2, (1.0, 1.0, 1.0))
        x3, y3 = (100, 200)
        x4, y4 = (400, 200)
        midpoint_line.midpoint(x3, y3, x4, y4, (1.0, 1.0, 1.0))
        midpoint_line.midpoint(x3, 300, x4, 300, (1.0, 1.0, 1.0))

    def draw_x(self, x, y, midpoint_line):
        r = 15
        x1, y1 = (x - r, y - r)
        x2, y2 = (x + r, y + r)
        midpoint_line.midpoint(x1, y1, x2, y2, (0.0, 1.0, 0.0))
        midpoint_line.midpoint(x1, y2, x2, y1, (0.0, 1.0, 0.0))

    def draw_o(self, x, y, midpoint_cir):
        midpoint_cir.set_circle_values(20, x, y)
        midpoint_cir.filled_circle(20, x, y)

    def checkForWinner(self, gameBoard):
        if (
            gameBoard[0][0] == 'X' and gameBoard[0][1] == 'X' and gameBoard[0][2] == 'X'
        ):
            return "X"
        elif (
            gameBoard[0][0] == 'O' and gameBoard[0][1] == 'O' and gameBoard[0][2] == 'O'
        ):
            return "O"
        elif (
            gameBoard[1][0] == 'X' and gameBoard[1][1] == 'X' and gameBoard[1][2] == 'X'
        ):
            return "X"
        elif (
            gameBoard[1][0] == 'O' and gameBoard[1][1] == 'O' and gameBoard[1][2] == 'O'
        ):
            return "O"
        elif (
            gameBoard[2][0] == 'X' and gameBoard[2][1] == 'X' and gameBoard[2][2] == 'X'
        ):
            return "X"
        elif (
            gameBoard[2][0] == 'O' and gameBoard[2][1] == 'O' and gameBoard[2][2] == 'O'
        ):
            return "O"
        if (
            gameBoard[0][0] == 'X' and gameBoard[1][0] == 'X' and gameBoard[2][0] == 'X'
        ):
            return "X"
        elif (
            gameBoard[0][0] == 'O' and gameBoard[1][0] == 'O' and gameBoard[2][0] == 'O'
        ):
            return "O"
        elif (
            gameBoard[0][1] == 'X' and gameBoard[1][1] == 'X' and gameBoard[2][1] == 'X'
        ):
            return "X"
        elif (
            gameBoard[0][1] == 'O' and gameBoard[1][1] == 'O' and gameBoard[2][1] == 'O'
        ):
            return "O"
        elif (
            gameBoard[0][2] == 'X' and gameBoard[1][2] == 'X' and gameBoard[2][2] == 'X'
        ):
            return "X"
        elif (
            gameBoard[0][2] == 'O' and gameBoard[1][2] == 'O' and gameBoard[2][2] == 'O'
        ):
            return "O"
        elif (
            gameBoard[0][0] == 'X' and gameBoard[1][1] == 'X' and gameBoard[2][2] == 'X'
        ):
            return "X"
        elif (
            gameBoard[0][0] == 'O' and gameBoard[1][1] == 'O' and gameBoard[2][2] == 'O'
        ):
            return "O"
        elif (
            gameBoard[0][2] == 'X' and gameBoard[1][1] == 'X' and gameBoard[2][0] == 'X'
        ):
            return "X"
        elif (
            gameBoard[0][2] == 'O' and gameBoard[1][1] == 'O' and gameBoard[2][0] == 'O'
        ):
            return "O"
        else:
            return "N"
    
    def toggle_play_mode(self):
      if self.mode == "AI":
        self.mode = "Player 2"
      else:
        self.mode = "AI"

    def mouse_callback(self, button, state, x, y):
        if state == GLUT_DOWN :
            if (x>=100 and x<=400) and (y>=100 and y<=400) and not self.game_over and not self.paused:
                self.x, self.y = x, y
                if not self.game_over and not self.draw and self.turnCounter % 2 == 0:
                   self.handle_mouse_click()
                if not self.game_over and not self.draw and self.turnCounter % 2 == 1:
                   self.handle_mouse_click2()
            else:
                if self.is_point(x,y,"x"):
                   glutDestroyWindow(glutGetWindow())
                   print(f"Goodbye")
                elif self.is_point(x,y,"||"):
                   self.paused = not self.paused
                elif self.is_point(x,y,"<-"):
                    print("Starting Over !")
                    self.game_over = False
                    self.draw = False
                    self.mode = "AI"
                    self.win = None
                    self.paused = True
                    self.rows = 3
                    self.cols = 3
                    self.x = 0
                    self.y = 0
                    self.turnCounter = 0
                    self.possibleNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                    self.gameBoard = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
                elif self.is_point(x,y,"<>"):
                    self.toggle_play_mode()

    # For Player no 1 
    def handle_mouse_click(self):     
        x, y, num = self.is_point_inside(self.x, self.y)
        if num in self.possibleNumbers:
            self.modifyArray(num, 'O')
            self.possibleNumbers.remove(num)
            self.turnCounter += 1
            self.check_and_handle_game_result()
    # For Player no AI/2
    def handle_mouse_click2(self):
        if self.mode=="Player 2":
           x, y, num = self.is_point_inside(self.x, self.y)
           if num in self.possibleNumbers:
             self.modifyArray(num, 'X')
             self.possibleNumbers.remove(num)
             self.turnCounter += 1
             self.check_and_handle_game_result()
        elif self.mode=="AI":
            best_move = self.find_best_move()
            if best_move != None:
                self.modifyArray(best_move[0] * 3 + best_move[1] + 1, 'X')
                self.possibleNumbers.remove(best_move[0] * 3 + best_move[1] + 1)
                self.turnCounter += 1
                self.check_and_handle_game_result()
                
    def draw_cross_and_circle(self, midpoint_line, midpoint_cir):
        for i in range(3):
            for j in range(3):
                if self.gameBoard[i][j] == 'X':
                    x, y, _ = self.is_point_inside(0, 0, i * 3 + j + 1)
                    self.draw_x(x, y, midpoint_line)
                elif self.gameBoard[i][j] == 'O':
                    x, y, _ = self.is_point_inside(0, 0, i * 3 + j + 1)
                    self.draw_o(x, y, midpoint_cir)

    def check_and_handle_game_result(self):
        winner = self.checkForWinner(self.gameBoard)
        if winner != "N":
            self.win= "Game Over!"+winner+" Won"
            self.draw_board(MidpointLine())
            self.draw_cross_and_circle(MidpointLine(), MidpointCircle())
            print("\nGame over! Thank you for playing :)")
            self.game_over = True
        elif len(self.possibleNumbers)==0:
            self.draw = True
            self.win="It's a draw try again!"

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        midpoint_line = MidpointLine()
        midpoint_cir = MidpointCircle()
        self.draw_board(midpoint_line)
        self.draw_xx(midpoint_line)
        self.draw_button(midpoint_line, self.paused)
        self.draw_arrow(midpoint_line)
        self.draw_cross_and_circle(midpoint_line, midpoint_cir)
        if self.game_over or self.draw:
            self.draw_game_over_text()

        glutSwapBuffers()

    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)

    def update(self, value):
        # if not self.game_over and not self.draw and self.turnCounter % 2 == 0 and not self.paused:
        #     self.handle_mouse_click2()   
        glutPostRedisplay()
        glutTimerFunc(16, self.update, 0)

    def main(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        glutCreateWindow("Tic-Tac-Toe Game")
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutMouseFunc(self.mouse_callback)
        glutTimerFunc(25, self.update, 0)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glutMainLoop()

if __name__ == "__main__":
    game_instance = Game()
    game_instance.main()
