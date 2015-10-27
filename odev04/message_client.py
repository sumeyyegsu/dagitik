__author__ = 'sumeyye'

'''CLIENT'''

import socket
import threading


# Bir thread icinde kendisine gelen mesajlari ekrana basacak
class readThread (threading.Thread):
    def __init__(self, clientSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
    
    def run(self):
        print 'Starting readThread'
        global closeFlag
        while not closeFlag:
            try:
                data = self.clientSocket.recv(buff)
            except:
                data = ''
            if data:
                print data
        self.clientSocket.close()


# Diger bir thread icinde kullanicidan giris bekleyip, gelen girisleri sunucuya gonderecek.
class writeThread (threading.Thread):
    def __init__(self, clientSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
    
    def run(self):
        print 'Starting writeThread'
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

rThread = readThread(client)
rThread.start()
wThread = writeThread(client)
wThread.start()
