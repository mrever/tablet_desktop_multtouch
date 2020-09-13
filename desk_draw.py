import socket
import numpy as np
import cv2

from common import Sketcher

h, w = 1500, 750
x, y = int(w/2), int(h/2)
mark = np.zeros((h, w, 3), np.uint8)
lineType = cv2.LINE_AA  # change it to LINE_8 to see non-antialiased graphics

host = ''
port = 55435  

server_socket = socket.socket()  
server_socket.bind((host, port))  

server_socket.listen()
conn, address = server_socket.accept()  
print("Connection from: " + str(address))
conn.settimeout(0.3)
cv2.imshow('drawing', mark)
while True:
    ch = cv2.waitKey(1)
    if ch == 27:
        break
    if ch == ord(' '):
        mark *= 0
        cv2.imshow('drawing', mark)
        continue
    try:
        data = conn.recv(1024).decode()
    except:
        continue
    if not data:
        break
    dsplit =  data.split(' ')
    if len(dsplit) > 7:
        prevx, prevy = x, y
        x, y = int(float(dsplit[-4])/2), int(float(dsplit[-2])/2)
        y += 200
        etype = dsplit[1][5:]
        print(x, y, etype)
        color = "%06x" % np.random.randint(0, 0xFFFFFF)
        color = tuple(int(color[i:i+2], 16) for i in (0, 2 ,4))
        if etype == "down" or etype == "up":
            cv2.circle(mark, (x, h-y), 3, color, 3, lineType)
        if etype == "move":
            cv2.line(mark, (x,h-y), (prevx, h-prevy), color, 3, lineType)

    data = 'dum' 
    conn.send(data.encode())  
    cv2.imshow('drawing', mark)

conn.close()  
cv2.destroyAllWindows()
