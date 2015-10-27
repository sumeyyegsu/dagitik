import socket
import threading
import random


# Bir thread i¸cinde kendisine gelen mesajları ekrana basacak.
class readThread (threading.Thread):
# ...
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 12345
        self.client = socket.socket()
        self.client.connect((self.host, self.port))
        self.text = ""

    def run(self):
        while 1:
            print('Client sent:', self.sock.recv(2048).decode())
            self.sock.send(b'Oi you sent something to me')

    def run(self):
        while True:
            try:
                data = self.client.recv(2048)
            except:
                break
            if data:
#                self.l.acquire()
                self.text = data
                print self.text
#                self.l.release()
        self.client.close()


# Diger bir thread icinde kullanıcıdan giris bekleyip, gelen girisleri sunucuya gonderecek.
# class writeThread (threading.Thread):
# ...

rThread = readThread()

rThread.start()

# wThread = writeThread(...)

# wThread.start()

# ...
