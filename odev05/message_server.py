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
    def __init__(self, logFileName):
        threading.Thread.__init__(self)
        self.fid = open(logFileName, "a")
    def log(self, message):
        self.fid.write(str(time.ctime()) + " - " + message)
        self.fid.flush()
    def run(self):
        self.log("Starting LogThread." + "\n")
        while True:
            if not logQueue.empty():
                self.log(str(logQueue.get()) + "\n")
        self.log("Exiting LogThread." + "\n")
        self.fid.close()
        
''' ------------------------------------------- MYREADTHREAD -------------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''

# socket dinliyor(parse edilmek icin gonderilen bir data var mi clienttan diye)
class myReadThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr, threadQueue, clientDict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.threadQueue = threadQueue
        self.clientDict = clientDict
        self.nickname = ""

# parser kuyruk mesajlari ve response'u uretecek        
    def parser(self, data):
        print ("PARSER START...")
        data = data.strip()
        logMessage = ""
          # kullanici ilk defa giris yapmak istiyorsa
        if data[0:3] == "USR" and self.nickname == "":
            nickname = data[4:]
            # client'in nickname'i bos degilse
            if nickname != "":
                # eger daha once login olmadiysa (fihristte yoksa onceden) fihriste ekleyecek
                if nickname not in clientDict.keys():
                    response = "HEL " + nickname
                    self.nickname = nickname
                    self.clientDict[self.nickname] = threadQueue
                    logMessage = self.nickname + " has joined."
                # daha once login olduysa reddedecek
                else:
                    response = "REJ " + nickname
            # nickname'i yazmayarak hatali bir komut yazmissa
            else:
                response = "ERR"

        # daha once login olduysa (self.nickname'i bos degilse)
        elif self.nickname != "":
            # cikis yapmak istiyorsa
            if data[0:3] == "QUI":
                # fihristten sil
                clientDict.pop(self.nickname)
                logMessage = self.nickname + " has left."
                response = "BYE " + self.nickname
            # login olmus client listesini istiyorsa
            elif data[0:3] == "LSQ":
                clients = ""
                # fihristi gezip key'leri(nickname) client degiskenine ekleyecek
                for key in self.clientDict.keys():
                    clients += key + ":"
                clients = clients[:-1]  # sondaki fazla :'yi siliyoruz
                response = "LSA " + clients
            # baglantiyi kontrol etmek istiyorsa
            elif data[0:3] == "TIC":
                response = "TOC"

            # genel mesaj gondermek istiyorsa
            elif data[0:3] == "SAY":
                print "client SAY dedi"
                for key in self.clientDict.keys():
                    if key != self.nickname:
                        self.clientDict[key].put(data)
                response = "SOK"

            # ozel mesaj gondermek istiyorsa
            elif data[0:3] == "MSG":
                print "client MSG dedi"
                key, message = str.split(data[4:], ":", 1)
                if key not in self.clientDict.keys():
                    response = "MNO"
                else:
                    self.clientDict[key].put("MGS " + self.nickname + ":" + message)
                    response = "MOK"
            # komut hataliysa
            else:
                response = "ERR"
        # henuz login olmadiysa
        else:
            response = "ERL"
        return response, logMessage

    def run(self):
        print 'Starting myReadThread-' + str(self.threadID)
        while True:
            try:
                try:
                    data = self.clientSocket.recv(buff)
                except:
                    data = ""
                if data:
                    response, logMessage = self.parser(data)
                    if response:
                            self.threadQueue.put(response)
                    if logMessage:
                            logQueue.put(logMessage)
            except:
                logQueue.put('Connection lost. Ending myReadThread-' + str(self.threadID) + "\n")
                break
        self.clientSocket.close()
        logQueue.put('Connection closed.' + "\n")


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
