__author__ = 'sumeyye'

''' SERVER '''
import socket
import threading
import datetime
import time

threadCounter = 0

class myThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.running = True
    def run(self):
        print 'Starting Thread-' + str(self.threadID)
#       ...
        while True:
            try:
                data = c.recv(2048)
            except:
                data = ""
            if not data:
                break

            for i in range(threadCounter):
                try:
                    c.send('Peki ' + str(addr[0]) + '\n')
                    currentTime = time.ctime(time.time()) + '\n'
                    c.send('Merhaba, saat su an ' + currentTime.encode('ascii')) #su an olan zamani istemciye gonderme
                except:
                    print 'Connection lost\n'
                    print 'Ending Thread-' + str(self.threadID)
                    self.threadID.remove(i)
        c.close()
#       ...

s = socket.socket()
print 'Socket created'
host = socket.gethostname()     # sunucunun adresi
port = 12345                    # dinleyecegi port numarasi
s.bind((host, port))            # bind islemi gerceklestirilir
print 'Socket bind complete'
s.listen(5)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)
print 'Socket now listening'
while True:
    print 'Waiting for connection'
    c, addr = s.accept()
    print 'Got a connection from' + str(addr)
    threadCounter += 1
    thread = myThread(threadCounter, c, addr)
    thread.start()
