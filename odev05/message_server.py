__author__ = 'sumeyye'
'''
        SUNUCU
                        '''

import socket
import threading
import Queue
import time


''' ------------------------------------------- MYLOGTHREAD ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------ '''
class myLogThread (threading.Thread):
    def __init__(self, logQueue, logFileName):
        threading.Thread.__init__(self)
        self.logQueue = logQueue
        self.fid = logFileName
    def log(self, message):
        self.fid = open(self.fid, "a")
        self.fid.write(str(time.ctime()) + " - " + message)
        self.fid.flush()
    def run(self):
        self.log("Starting LogThread")
        while True:
            if not self.logQueue.empty():
                self.log(self.logQueue.get() + "\n")
        self.log("Exiting LogThread")
        self.fid.close()
        
''' ------------------------------------------- MYREADTHREAD -------------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
#socket dinliyor
class myReadThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr, threadQueue, logQueue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.threadQueue = threadQueue
        self.logQueue = logQueue
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
            response = "TOC"
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
# kuyruk dinliyor
class myWriteThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr, threadQueue, logQueue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.threadQueue = threadQueue
        self.logQueue = logQueue
    def run(self):
        print 'Starting myWriteThread-' + str(self.threadID)
        while True:
            # ...
            # sirada mesaj varsa
            if self.threadQueue.qsize() > 0:
                queueMessage = self.threadQueue.get()
                # gonderilen ozel mesajsa => nickname:message
                if ':' in queueMessage:
                    messageToSend = "MSG " + queueMessage[0] + ":" + queueMessage[1]
                    fihrist[queueMessage[0]]
                # genel mesajsa => message
                elif queueMessage[1]:
                    messageToSend = "SAY "
                # hicbiri degilse sistem mesajidir.
                else:
                    messageToSend = "SYS "
            # ...
        self.logQueue.put("Exiting myWriteThread-" + self.threadID)
  
        
        
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

lqueue = Queue.Queue()
logThread = myLogThread(lqueue, "log.txt")      # log icin thread yaratiyoruz
logThread.start()                               # threadi baslatiyoruz

while True:
    print 'Waiting for connection. Listenin port ' + str(port) + ' ...'
    c, addr = s.accept()
    print 'Got a connection from' + str(addr)
    
    queue = Queue.Queue()

    threadCounter += 1
    readThread = myReadThread(threadCounter, c, addr, queue, lqueue)
    readThread.start()

    writeThread = myWriteThread(writeThreadCounter, c, addr, queue, lqueue)
    writeThread.start()
