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
    def run(self):
        print 'Starting Thread-' + str(self.threadID)
        while True:
            try:
                try:
                    data = c.recv(buff)
                except:
                    data = ''
                if data:
                    c.send('Peki ' + str(addr[0]) + '\n')
                if random.randint(1, 10) == 5:
                    c.send('Merhaba, saat su an ' + time.strftime("%H:%M:%S") + '\n') #su an olan zamani istemciye gonderme
            except:
                print 'Connection lost\n'
                print 'Ending Thread-' + str(self.threadID)
                break
            if 'close' == data.rstrip():
                break
        self.clientSocket.close()
        print 'Connection closed.'

threadCounter = 0
buff = 2048
s = socket.socket()
print 'Socket created'
host = socket.gethostname()     # sunucunun adresi
port = 12345                    # dinleyecegi port numarasi
s.bind((host, port))            # bind islemi gerceklestirilir
print 'Socket bind complete'
s.listen(5)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)
print 'Socket now listening'
while True:
    print 'Waiting for connection. Listenin port ' + str(port) + ' ...'
    c, addr = s.accept()
    print 'Got a connection from' + str(addr)
    threadCounter += 1
    thread = myThread(threadCounter, c, addr)
    thread.start()
