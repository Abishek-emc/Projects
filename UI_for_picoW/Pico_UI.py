from machine import Pin, I2C, UART,ADC
from ssd1306 import SSD1306_I2C
import time
import random
import framebuf
#-----------------------------------------------classes and functions--------------------------------------#
class node:
    def __init__(self,name,content,typ,parent):
        self.child =[]
        self.content2display = content
        self.type = typ
        self.name = name
        self.parent = parent
        self.state = 0
    def add_child(self,page):
        self.child.append(page)
    def display(self,value):
        dis.fill(0) 
        if self.type == "menu":
            dis.text(self.name, 35, 0)
            for i, item in enumerate(self.child):
                dis.text(f"{item.name}", 10, 10 + 10*i)
                dis.rect(0, 8 + 10*value, 128, 11, 1)
            dis.show()
        elif self.type == "home":                    
            with open("pickachu.pbm","rb") as f:
                f.readline()
                f.readline()
                f.readline()
                buffer = bytearray(f.read())
            fb = framebuf.FrameBuffer(buffer,128,64, framebuf.MONO_HLSB)
            dis.fill(1)
            dis.blit(fb,0,0)
            dis.show()
        elif self.type == "game":
            if self.name == "XO":
                XO_game()
            elif self.name == "Snake&Egg":
                snake_game()
                
        elif self.type == "button":
            old = 1
            while not (v_x.read_u16()<5000):
                new = sw.value()
                if old==1 and new == 0:
                    self.state = not(self.state)
                    if self.name == "Flash":
                        if self.state:
                            dis.fill(0)
                            dis.text("Flash ON !",10,10)
                            led.value(1)
                        else:
                            dis.fill(0)
                            dis.text("Flash OFF !",10,10)
                            led.value(0)
                    elif self.name == "Mode":
                        if self.state:
                            dis.fill(0)
                            dis.text("Light mode!",10,10)
                            dis.invert(1)
                        else :
                            dis.fill(0)
                            dis.text("Dark mode!",10,10)
                            dis.invert(0)
                            
                old = new
                dis.show()
        elif self.type == "call":
            dis.fill(0)
            dis.text(f"{self.name}",30,10)
            dis.text(f"{self.content2display}",20,20)
            dis.text("calling...",30,30)
            dis.text("hang",0,54)
            make_call(b'{self.content2display}')
                                              #function to make a call
            dis.show()
        elif self.type == "message":
            dis.fill(0)
            dis.text("message sent",20,20)
            dis.text("successfully!!!",7,30)
                                              #fuction to send message        
            dis.show()
            
def send_at_command(command):
    uart.write(command + b'\r\n')
    time.sleep(1)  
    response = uart.read()
    return response

def make_call(phone_number):
    command = b'ATD' + phone_number + b';'
    response = send_at_command(command)
    print(response)

def read_joystick():
    x = v_x.read_u16()
    y = v_y.read_u16()
    button = sw.value()
    return x, y, button

def move_b(current_node):
    if current_node.parent != None :
        return current_node.parent
def move_f(current_node,position):
    if (position < len(current_node.child) and position>0) and len(current_node.child):
        return current_node.child[position]
def XO_game():
    global cursor_x, cursor_y
    oled = dis
    dis.fill(0)
    x_axis = ADC(Pin(26))  
    y_axis = ADC(Pin(27))  
    button = Pin(6, Pin.IN, Pin.PULL_UP)  
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'
    game_over = False

    def draw_board():
        oled.fill(0)
        for i in range(4):
            oled.line(i * 42, 0, i * 42, 63, 1)
            oled.line(0, i * 21, 127, i * 21, 1)
        for y in range(3):
            for x in range(3):
                if board[y][x] != ' ':
                    oled.text(board[y][x], x * 42 + 16, y * 21 + 6)
        oled.rect(cursor_x * 42, cursor_y * 21, 42, 21, 1)
        oled.show()

    def check_winner():
        global game_over
        for line in board + list(map(list, zip(*board))) + [[board[i][i] for i in range(3)], [board[i][2 - i] for i in range(3)]]:
            if line.count(line[0]) == 3 and line[0] != ' ':
                game_over = True
                return line[0]
        if all(board[y][x] != ' ' for y in range(3) for x in range(3)):
            game_over = True
            return 'Draw'
        return None

    def update_cursor():
        global cursor_x, cursor_y
        x_val = x_axis.read_u16()
        y_val = y_axis.read_u16()
        
        if x_val < 20000:
            cursor_x = max(0, cursor_x - 1)
        elif x_val > 60000:
            cursor_x = min(2, cursor_x + 1)
        
        if y_val < 20000:
            cursor_y = max(0, cursor_y - 1)
        elif y_val > 60000:
            cursor_y = min(2, cursor_y + 1)

    while not game_over:
        draw_board()
        update_cursor()
        
        if button.value() == 0:
            if board[cursor_y][cursor_x] == ' ':
                board[cursor_y][cursor_x] = current_player
                winner = check_winner()
                if winner:
                    oled.fill(0)
                    if winner == 'Draw':
                        oled.text("Draw!", 45, 30)
                    else:
                        oled.text(f"{winner} wins!", 30, 30)
                    oled.show()
                    time.sleep(2)
                    break
                current_player = 'O' if current_player == 'X' else 'X'
            time.sleep(0.3)  
        time.sleep(0.1)  
    oled.fill(0)
    oled.text("Game Over", 30, 30)
    oled.show()
    
def snake_game():
    global cursor_x, cursor_y, width, height, snake, snake_dir, food, game_over
    i2c = I2C(1, scl=Pin(3), sda=Pin(2))
    oled = dis    
    x_axis = v_x  
    y_axis = v_y  
    button = sw  
    cursor_x, cursor_y = 0, 0
    width, height = 128, 64
    snake = [(64, 32)]
    snake_dir = (1, 0)
    food = (random.randint(0, width // 8 - 1) * 8, random.randint(0, height // 8 - 1) * 8)
    game_over = False

    def draw():
        oled.fill(0)
        for segment in snake:
            oled.fill_rect(segment[0], segment[1], 8, 8, 1)
        oled.fill_rect(food[0], food[1], 8, 8, 1)
        oled.show()

    def move_snake():
        global snake, food, game_over, snake_dir
        head_x, head_y = snake[0]
        new_head = ((head_x + snake_dir[0] * 8) % width, (head_y + snake_dir[1] * 8) % height)
        if new_head in snake:
            game_over = True
            return
        snake.insert(0, new_head)
        if new_head == food:
            food = (random.randint(0, width // 8 - 1) * 8, random.randint(0, height // 8 - 1) * 8)
        else:
            snake.pop()

    def change_direction():
        global snake_dir
        x_val = x_axis.read_u16()
        y_val = y_axis.read_u16()
        
        if x_val < 20000 and snake_dir != (1, 0):
            snake_dir = (-1, 0)
        elif x_val > 60000 and snake_dir != (-1, 0):
            snake_dir = (1, 0)
        elif y_val < 20000 and snake_dir != (0, 1):
            snake_dir = (0, -1)
        elif y_val > 60000 and snake_dir != (0, -1):
            snake_dir = (0, 1)
    while not game_over:
        change_direction()
        move_snake()
        draw()
        time.sleep(0.2)
    oled.fill(0)
    oled.text("Game Over", 30, 30)
    oled.show()    
    
    
    
########################## Pin and protocal declaration ###############################
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
dis = SSD1306_I2C(128, 64, i2c)
uart = UART(1, baudrate=9600, tx=4, rx=5)
v_x = ADC(26)
v_y = ADC(27)
sw = Pin(6,Pin.IN,Pin.PULL_UP)
led = Pin("LED",Pin.OUT)
cursor_x, cursor_y = 0,0
#######################################################################################   
#------------------------------------------------list declaration----------------------------------------------------------#


main_list = ["Contact","Flash","Game","Mode","Shareloc"]
contacts = {"joythev":"9677058049","nara":"8072979821","barath":"9600873491"}
names = contacts.keys()
#--------------------------------------page declaration----------------------------------------------------#

#___________________________layer 0_________________________________________
home = node("home page"," welcome ","home",None)
#___________________________layer 1_________________________________________
main_menu = node("main menu",main_list,"menu",home)
home.add_child(main_menu)
#___________________________layer 2_________________________________________
contact = node("Contacts",contacts.keys(),"menu",main_menu)
flash = node("Flash",contacts.keys(),"button",main_menu)
game = node("Game",["tic tac toe","snake game"],"menu",main_menu)
shareloc = node("Shareloc",contacts.keys(),"menu",main_menu)
mode = node("Mode","set the mode","button",main_menu)
main_menu.add_child(contact)
main_menu.add_child(flash)
main_menu.add_child(game)
main_menu.add_child(shareloc)
main_menu.add_child(mode)
#___________________________layer 3_________________________________________
XO = node("XO","nothing","game",game)
snakes = node("Snake&Egg",["nothing"],"game",game)
game.add_child(XO)
game.add_child(snakes)
contact_obj = []
for i in names:
    j = node(i,contacts[i],"message",shareloc)
    i = node(i,contacts[i],"call",contact)
    contact.add_child(i)
    shareloc.add_child(j)
    contact_obj.append(i)
    

current_node = home
position  = 0
dis.invert(1)
while True:
    x,y,switch = read_joystick()
    if y<5000 and position>0:
        position -=1
    elif y>60000 and  position<len(current_node.child)-1:
        position +=1
    elif switch == 0:
        if current_node.name == "home page":
            current_node = current_node.child[0]    
        elif len(current_node.child)>0:    
            current_node = current_node.child[position]
        position = 0    
    elif x<5000 and current_node!= home:
        current_node = move_b(current_node)
    #display-------------------------------------------------------------
    dis.fill(0)
    current_node.display(position)
    if current_node.type == "button" or current_node.type == "game" :
        current_node = move_b(current_node)
        position = 0
    dis.show()
    time.sleep(0.1)