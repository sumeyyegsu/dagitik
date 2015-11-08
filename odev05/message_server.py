__author__ = 'sumeyye'
'''
        SUNUCU
                        '''

import socket
import threading


''' ------------------------------------------- PARSER -------------------------------------------------------- '''
''' ----------------------------------------------------------------------------------------------------------- '''
def parser(self, data):
    print ("PARSER START...")
    data = data.strip()
    
    nickname = data[4:]
    newdict = {nickname:data}
    
    # ilk kod 3 karakterden olusmuyorsa
    if not data[3] == " ":
        response = "ERR"
        return response

     if data[0:3] == "USR":
        # kullanici fihristte yoksa eklenecek
        if nickname not in fihrist:
            response = "HEL " + nickname
            # fihristi guncelle
            self.fihrist.update(newdict)
            return response
        # kullanici zaten fihristte varsa reddedilecek
        else:
            response = "REJ " + nickname
            return response
    elif data[0:3] == "QUI":
        response = "BYE " + self.nickname
        # fihristten sil
        fihrist.pop(newdict)
        return response
    elif data[0:3] == "LSQ":
        print "LSQ"
        # ...
    elif data[0:3] == "TIC":
        response "T0C"
        return response
    elif data[0:3] == "SAY":
        print "SAY"
        # ...
    elif data[0:3] == "MSG":
        print "MGS"
    else:
        # bir seye uymadiysa protokol hatasi verilecek
        response = "ERR"
        return response

''' ------------------------------------------- MYREADTHREAD -------------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''

class myReadThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
    def run(self):
        print 'Starting myReadThread-' + str(self.threadID)
        while True:
            try:
                try:
                    data = self.clientSocket.recv(buff)
                except:
                    data = ''
                if data:
                    parser(self, data)
            except:
                print 'Connection lost. Ending myReadThread-' + str(self.threadID)
                break
        self.clientSocket.close()
        print 'Connection closed.'

''' ------------------------------------------- MYWRITETHREAD -------------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------------ '''

class myWriteThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
    def run(self):
        print 'Starting myWriteThread-' + str(self.threadID)
        while True:
'''
            try:
                try:
                    data = self.clientSocket.recv(buff)
                except:
                    data = ''
                if data:
                     # parser(self, data)
            except:
                print 'Connection lost. Ending myWriteThread-' + str(self.threadID)
                break
'''
        self.clientSocket.close()
        print 'Connection closed.'
        
fihrist = {}    #fihristin tanimlanmasi

threadCounter = 0
buff = 2048

s = socket.socket()             # socket yaratiyoruz
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
    print 'Got a connection from' + str(addr)

    readThreadCounter += 1
    readThread = myReadThread(readThreadCounter, c, addr)
    readThread.start()

    writeThreadCounter += 1
    writeThread = myWriteThread(writeThreadCounter, c, addr)
    writeThread.start()
