import numpy as np
import socket
from _thread import *
from snake import SnakeGame
import uuid
import time
import threading

# server = "10.11.250.207"
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientList = []
counter = 0 
rows = 20 

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
# s.settimeout(0.5)
print("Waiting for a connection, Server Started")




game = SnakeGame(rows)
game_state = "" 
last_move_timestamp = time.time()
interval = 0.2
moves_queue = set()

def game_thread() : 
    global game, moves_queue, game_state 
    while True :
        last_move_timestamp = time.time()
        game.move(moves_queue)
        moves_queue = set()
        game_state = game.get_state()
        while time.time() - last_move_timestamp < interval : 
            time.sleep(0.1) 

def sendMsg(msg):
    message = 'm' + msg  # Format the message with a prefix
    for c in clientList:
        try:
            c.send(message.encode())
        except Exception as e:
            print(f"could not send message: {e}")

rgb_colors = {
    "red" : (255, 0, 0),
    "green" : (0, 255, 0),
    "blue" : (0, 0, 255),
    "yellow" : (255, 255, 0),
    "orange" : (255, 165, 0),
} 
rgb_colors_list = list(rgb_colors.values())

def main(conn, clientList) : 
    global counter, game

    unique_id = str(uuid.uuid4())
    color = rgb_colors_list[np.random.randint(0, len(rgb_colors_list))]
    game.add_player(unique_id, color = color) 

    start_new_thread(game_thread, ())
    
    while True : 
        type = conn.recv(1).decode()
        if(type == 'c'):
            data = conn.recv(1).decode()
            move = None 
            if not data :
                #print("no data received from client")
                break 
            elif data == "g" : 
                print("received get")
                pass 
            elif data == "q" :
                print("received quit")
                game.remove_player(unique_id)
                break
            elif data == "r" : 
                game.reset_player(unique_id)

            elif data == "N" : 
                move = "up"
                moves_queue.add((unique_id, move))
            elif data == "S" : 
                move = "down"
                moves_queue.add((unique_id, move))
            elif data == "E" : 
                move = "right"
                moves_queue.add((unique_id, move))
            elif data == "W" : 
                move = "left"
                moves_queue.add((unique_id, move))
            else :
                print("Invalid data received from client:", data)
            gs_len = str(len(game_state)).zfill(100)
            gs_header = 'g' + gs_len + game_state
            conn.send(gs_header.encode())
        elif(type == 'm'):
            msglen = conn.recv(2).decode()
            msg = conn.recv(int(msglen)).decode()
            #broadcast message
            print("*****--->recieved: "+msg)
            reformat_msg = type + msglen + msg
            sendMsg(reformat_msg)
            pass
        
        
            
    conn.close()

if __name__ == "__main__" : 
    while True:
        conn, addr = s.accept()
        clientList.append(conn)
        connectionThread = threading.Thread(target=main, args=(conn, clientList))
        connectionThread.start()