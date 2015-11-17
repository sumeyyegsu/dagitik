__author__ = 'sumeyye'

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
                    self.clientDict[self.nickname] = self.threadQueue
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
                clients = clients[:-1]
                response = "LSA " + clients
            # baglantiyi kontrol etmek istiyorsa
            elif data[0:3] == "TIC":
                response = "TOC"

            # genel mesaj gondermek istiyorsa
            elif data[0:3] == "SAY":
                for key in self.clientDict.keys():
                    if key != self.nickname:
                        self.clientDict[key].put(data)
                response = "SOK"

            # ozel mesaj gondermek istiyorsa
            elif data[0:3] == "MSG":
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
        logQueue.put('Starting myReadThread-' + str(self.threadID))
        while True:
            data = self.clientSocket.recv(buff)
            print "Server'a gelen data: " + data
            response, logMessage = self.parser(data)
            if logMessage:
                logQueue.put(logMessage)
            if response:
                self.threadQueue.put(response)

''' ------------------------------------------- MYWRITETHREAD -------------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------------ '''
# kuyruk dinliyor
class myWriteThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr, clientDict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.clientDict = clientDict
    def run(self):
        logQueue.put('Starting myWriteThread-' + str(self.threadID))
        acceptedList = ['HEL', 'REJ', 'BYE', 'LSA', 'TOC', 'SOK', 'MOK', 'MNO', 'ERR', 'ERL']
        while True:
            queueMessage = str(threadQueue.get())
            # gonderilen ozel mesaj ve ya genel mesajsa
            if queueMessage[0:3] not in acceptedList:
                messageToSend = queueMessage[4:]
            # ozel ya da genel mesaj degilse
            else:
                messageToSend = queueMessage
            print "Server'dan gonderilen data: " + messageToSend
            self.clientSocket.send(messageToSend)
        logQueue.put("Exiting myWriteThread-" + self.threadID + "\n")
  
        
        
clientDict = {}
threads = []
threadCounter = 0
buff = 2048
logQueue = Queue.Queue()

s = socket.socket()             # socket yaratiyoruz
logQueue.put('Socket created.')
host = socket.gethostname()     # sunucunun adresi
port = 12345                    # dinleyecegi port numarasi
s.bind((host, port))            # bind islemi gerceklestirilir
s.listen(5)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)

# logThread'i yaratip, thread listesine ekleyip baslatiyoruz
logThread = myLogThread("log.txt")
threads.append(logThread)
logThread.start()

while True:
    c, addr = s.accept()
    logQueue.put('Got a connection from ' + str(addr))
    
    threadQueue = Queue.Queue()

    threadCounter += 1
    readThread = myReadThread(threadCounter, c, addr, threadQueue, clientDict)
    readThread.daemon = True
    threads.append(readThread)
    readThread.start()

    writeThread = myWriteThread(threadCounter, c, addr, clientDict)
    writeThread.daemon = True
    threads.append(writeThread)
    writeThread.start()
    
for t in threads:
    t.join()
