import socket
import threading
import random


# Bir thread icinde kendisine gelen mesajlari ekrana basacak
class readThread (threading.Thread):
# ...
    def __init__(self):
        super(readThread, self).__init__()
        self.host = socket.gethostname()
        self.port = 12345
        self.client = socket.socket()
        self.client.connect((self.host, self.port))
        self.text = ""
        
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


# Diger bir thread icinde kullanicidan giris bekleyip, gelen girisleri sunucuya gonderecek.
# class writeThread (threading.Thread):
# ...

rThread = readThread()

rThread.start()

# wThread = writeThread(...)

# wThread.start()

# ...
