__author__ = 'sumeyye'

'''CLIENT'''

import socket
import threading

# client bu thread icinde, server'dan gelen mesajlari ekrana basacak.
class receiveFromServerThread (threading.Thread):
    def __init__(self, clientSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
    
    def run(self):
        print 'Starting Thread-Receive From Server'
        global closeFlag
        while not closeFlag:
            try:
                data = self.clientSocket.recv(buff)
            except:
                data = ''
            if data:
                print data
        self.clientSocket.close()


# client bu thread icinde, kullanicidan giris bekleyip, gelen girisleri server'a gonderecek.
class sendToServerThread (threading.Thread):
    def __init__(self, clientSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
    
    def run(self):
        print 'Starting Thread-Send To Server.'
        global closeFlag
        while not closeFlag:
            data = raw_input()
            if data:
                self.clientSocket.send(data)
                if data == 'close':
                    closeFlag = 1
        self.clientSocket.close()
        print 'Client closed.'

buff = 2048
closeFlag = 0 
host = socket.gethostname()
port = 12345
client = socket.socket()
client.connect((host, port))

rThread = receiveFromServerThread(client)
rThread.start()
sThread = sendToServerThread(client)
sThread.start()
