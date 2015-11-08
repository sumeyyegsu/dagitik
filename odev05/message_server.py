__author__ = 'sumeyye'
'''
        SUNUCU
                        '''

import socket
import threading

''' ------------------------------------------- PARSER -------------------------------------------------------- '''
''' ----------------------------------------------------------------------------------------------------------- '''
def parser(self, data):
    print ("PARSER START..."
           "")
    data = data.strip()
    newdict = {}
    # henuz login olmadiysa
    if not self.nickname and not data[0:3] == "USR":
        print "NOT USER NOT NICKNAME"
        # ...

    # data sekli bozuksa --> XXX BLABLABLA yani 4. karakter bosluk degilse forma uygunde degildir
    # daha sonra 'istek listesinde' degilse de bozuktur diyebiliriz
    if not data[3] == " ":
        response = "ERR"
        self.csend(response)
        return 0

    if data[0:3] == "USR":
        nickname = data[4:]
        # kullanici yoksa
        if nickname not in fihrist:
            response = "HEL " + nickname
            # ...
            print 'response: ' + self.nickname
            # fihristi guncelle
            newdict = {nickname:data}
            self.fihrist.update(newdict)
            # ...
            self.lQueue.put(self.nickname + " has joined.")
            return 0
        else:
            # kullanici reddedilecek
            response = "REJ " + nickname
            self.csend(response)
            # ...
            # baglantiyi kapat
            self.csoc.close()
            return 1
    elif data[0:3] == "QUI":
        response = "BYE " + self.nickname
        # ...
        # fihristten sil
        fihrist.pop(newdict)
        # log gonder
        # ...
        # baglantiyi sil
        # ...
        # ...
    elif data[0:3] == "LSQ":
        response = "LSA "
        # ...
    elif data[0:3] == "TIC":
        print "TIC"
        # ...
    elif data[0:3] == "SAY":
        print "SAY"
        # ...
    elif data[0:3] == "MSG":
        # ...
        '''
        if not to_nickname in self.fihrist.keys():
            response = "MNO"
        else:
            queue_message = (to_nickname, self.nickname, message)
            # gonderilecek threadQueueyu fihristten alip icine yaz
            self.fihrist[to_nickname].put(queue_message)
            response = "MOK"
            self.csend(response)
        '''
    else:
        # bir seye uymadiysa protokol hatasi verilecek
        response = "ERR"
        # ...

''' ------------------------------------------- MYTHREAD -------------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''

# clientlara cevap vermesi icin yaratilacak threadlerin class'i
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
                    data = self.clientSocket.recv(buff)
                except:
                    data = ''
                if data and (not data == 'close'):
                    self.clientSocket.send('Peki ' + str(self.clientAddr[0]) + ' - ' + str(self.clientAddr[1]))
                    parser(self, data)
            except:
                print 'Connection lost\n'
                print 'Ending Thread-' + str(self.threadID)
                break
            if 'close' == data.rstrip():
                break
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
