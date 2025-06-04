from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import socket
import pygame
import threading
import tkinter as tk
import queue


server_addr = "localhost"
server_port = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_addr, server_port))
width = 500
rows = 20
window = pygame.display.set_mode((width,width))
game_state_queue = queue.Queue()
message_queue = queue.Queue()



def recieveState():  
    game_state = client_socket.recv(500).decode()
    return game_state
    

def redrawSquares(game_state, surface):
    data = game_state.split("|", 1)
    snakes = data[0].split("**")
    num_snakes = len(snakes)
    for s in range(num_snakes):
        x = s%3
        if x == 0:
            r=255
            g=128
            b=0
        elif x == 1:
            r=255
            g=255
            b=0
        elif x == 2:
            r=0
            g=255
            b=0
        snake = snakes[s].split("*")
        size_of_snake = len(snake)
        for i in range (size_of_snake):
            strip_snake = snake[i].strip("()")
            snakebody = strip_snake.split(",")
            coordinate_1 = int(snakebody[0]) * 25
            coordinate_2 = int(snakebody[1]) * 25
            cube = pygame.Rect(coordinate_1, coordinate_2, 25, 25)
            pygame.draw.rect(surface, (r,g,b), cube)
    snack = data[1].split("**")
    num_snacks = len(snack)
    for i in range (num_snacks):
        strip_snack = snack[i].strip("()")
        snack_square = strip_snack.split(",")
        coordinate_1 = int(snack_square[0]) * 25
        coordinate_2 = int(snack_square[1]) * 25
        cube = pygame.Rect(coordinate_1, coordinate_2, 25, 25)
        pygame.draw.rect(surface, (255, 0, 0), cube)


def redrawWindow(surface,width,rows):
    row_space = width//rows
    x=0
    y=0
    for i in range (rows):
        x += row_space
        y += row_space
        pygame.draw.line(surface, (255,255,255), (x,0),(x,width))
        pygame.draw.line(surface, (255,255,255), (0,y),(width,y))
    
    

def sendMove(move):
    client_socket.send(move.encode())

def sendMsg(msg):
    client_socket.send(msg.encode())

def network_thread(game_state_queue):
    while True:
        # Receive data from the server
        try:

            type = client_socket.recv(1).decode()

            if type == 'm':  # If it's a message
                msg_len = client_socket.recv(2).decode()
                if 'm' in msg_len:
                    l1 = msg_len.strip('m')
                    l2 = client_socket.recv(1).decode()
                    msg_len = l1+l2
                msg = client_socket.recv(int(msg_len)).decode()
                message_queue.put(msg)
            elif type == 'g':
                gs_len = client_socket.recv(100).decode()
                gs = client_socket.recv(int(gs_len)).decode()
                game_state_queue.put(gs)
        except Exception as e:
            print(f"Network thread error: {e}")
            break

def main():
    
    net_thread = threading.Thread(target=network_thread, args=(game_state_queue,))
    net_thread.start()
    sendMove("cg")
    while(True):
        
        move = "cg"
        msg = ""
        if not game_state_queue.empty():
            curr_game_state = game_state_queue.get()
            window.fill((0,0,0))
            redrawSquares(curr_game_state, window)
            redrawWindow(window,width,rows)
        
        while not message_queue.empty():
            rcv_message = message_queue.get()
            print("--------->" + rcv_message)
        
        
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            for key in keys:
                if keys[pygame.K_LEFT]:
                    move="cW"
                elif keys[pygame.K_RIGHT]:
                    move="cE"
                elif keys[pygame.K_UP]:
                    move="cN"
                elif keys[pygame.K_DOWN]:
                    move="cS"
                elif keys[pygame.K_r]:
                    move="cr"
                elif keys[pygame.K_q]:
                    move="cq"
                    sendMove(move)
                    client_socket.close()
                    break
                elif keys[pygame.K_z]:
                    msg="m06ready?"
                elif keys[pygame.K_x]:
                    msg="m08nice try!"
                elif keys[pygame.K_c]:
                    msg="m10we did it!"

        sendMove(move)
        if(msg != ""):
            sendMsg(msg)
        pygame.display.update() 
            
if __name__ == "__main__":
    main()