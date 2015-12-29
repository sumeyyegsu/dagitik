__author__ = 'sumeyye'

import threading
import socket
import Queue
import time
import copy
from time import strftime

''' --------------------------------------- PEER CLIENT THREAD -------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''


''' ---------------------------------------- TEST PEER CONNECTION THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''


''' ----------------------------------------PEER SERVER THREAD-------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Es - sunucu tarafi
class myPeerServerThread (threading.Thread):
    def __init__(self, threadQueue):
        threading.Thread.__init__(self)
        self.threadQueue = threadQueue
        self.port = 10000               # dinleyecegi port numarasi
        self.host = "127.0.0.5"         # sunucunun adresi
    def run(self):
        s = socket.socket()             # socket yaratiyoruz
        s.bind((self.host, self.port))  # bind islemi gerceklestirilir
        s.listen(4)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)
        while True:
            c,addr = s.accept()
            negotiatorServerReceiveThread = myNegotiatorServerReceiveThread(c, addr, self.threadQueue)
            negotiatorServerReceiveThread.start()

''' -------------------------------------- NEGOTIATOR SERVER RECEIVE THREAD ------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''

class myNegotiatorServerReceiveThread(threading.Thread):
    def __init__(self, peerSocket, peerAddr, threadQueue):
        threading.Thread.__init__(self)
        self.peerSocket = peerSocket
        self.peerAddr = peerAddr
        self.threadQueue = threadQueue
        self.flagRegistration = False

    def run(self):
        global CONNECT_POINT_LIST
        while True:
            try:
                receivedData = str(self.peerSocket.recv(buff))
                if receivedData:
                    self.parser(receivedData)
            except socket.timeout:
                self.peerSocket.close()
                break

    def parser(self, receivedData):
        receivedData = receivedData.strip()
        # herhangi bir uc'tan HELLO gelirse SALUT cevabini yolluyoruz.
        if (receivedData[:5] == "HELLO"):
            self.peerSocket.send("SALUT")

        # herhangi bir birimden CLOSE gelirse, BUBYE deyip baglantimizi kapatiyoruz.
        elif (receivedData[:5] == "CLOSE"):
            self.peerSocket.send("BUBYE")
            self.peerSocket.close()
            if self.peerAddr in CONNECT_POINT_LIST.keys():
                CONNECT_POINT_LIST.pop(self.peerAddr)

        # REGME komutu geldiyse
        elif (receivedData[:5] == "REGME"):
            host, port = str.split(receivedData[6:], ':', 1)
            port = int(port)
            # peer listede zaten varsa
            if (host, port) in CONNECT_POINT_LIST.keys():  # ex: N-S:123213546
                value = CONNECT_POINT_LIST[(host, port)]
                value[2:] = "S:" + str(time.time())
                CONNECT_POINT_LIST[(host, port)] = value
                self.peerSocket.send("REGOK " + str(value[4:]))
                self.flagRegistration = True
                
            # peer listede yoksa
            else:
                # kaydi beklemeye aliyoruz
                self.peerSocket.send("REGWA")
                CONNECT_POINT_LIST[(host, port)] = "?-W:" + str(time.time())  ##P mi N mi neye gore ekleyecegiz???
                self.peerSocket.close()

        # GETNL : negotiator'in listesi istendiyse
        elif (receivedData[:5] == "GETNL"):
            if self.flagRegistration:
                nlsize = int(receivedData[6:])
                if nlsize == 0:
                    nlsize = 50 #nlsize tanimlanmadigi yerde 50 kabul edilir.
                self.peerSocket.send("NLIST BEGIN\n")
                i = 0
                for key, value in CONNECT_POINT_LIST.iterkeys():
                    if i <= nlsize:
                        data = str(key[0]) + ":" + str(key[1]) + ":"\
                            + str(value[0]) + ":" + str(value[4:]) + "\n"
                        self.peerSocket.send(data)
                        i += 1
                self.peerSocket.send("NLIST END")
            else:
                self.peerSocket.send("REGER")
                
        # FUNRQ : peer'in bir fonksiyonu istendiyse/ var mi diye bakildiysa
        elif (receivedData[:5] == "FUNRQ"):
            if self.flagRegistration:
                functionname = str(receivedData[6:])
                print "S_PEER: GETNL geldi. functionname: " + functionname
                if functionname in functionList:
                    self.peerSocket.send("FUNYS " + functionname)
                    print "S_PEER: Baglanti uzerinden gonderilen: " + "FUNYS " + functionname
                else:
                    self.peerSocket.send("FUNNO " + functionname)
                    print "S_PEER: Baglanti uzerinden gonderilen: " + "FUNNO " + functionname
            else:
                self.peerSocket.send("REGER")
                print "S_PEER: Baglanti uzerinden gonderilen: REGER"
                
        # EXERQ
        elif (receivedData[:5] == "EXERQ"):
            if self.flagRegistration:
            else:
                self.peerSocket.send("REGER")
                
        # PATCH 
        elif (receivedData[:5] == "PATCH"):
            if self.flagRegistration:
            else:
                self.peerSocket.send("REGER")
                
        #diger tum durumlarda
        else:
            print "S_NEGOTIATOR: CMDER gonderiliyor."
            self.peerSocket.send("CMDER")
            print "S_NEGOTIATOR: Baglanti kapatiliyor."
            self.peerSocket.close()


#buffer buyuklugu
buff = 2048
# Baglanti listesi
CONNECT_POINT_LIST = {} #{[addr1,type1-S:time1],[addr2,type2-W:time2],...} yani KEY = (host,port) ve VALUE = type-status:time
# CONNECT_POINT_LIST'in bir sonraki guncellemesinden onceki bekleme suresi
UPDATE_INTERVAL = 20
# kilit mekanizmasi
pLock = threading.Lock()
# peer'in sahip oldugu fonksiyonlarin listesi
functionList = ['Gray Scale Filter', 'Sobel Filter', 'Binarize Filter', 'Prewitt Filter', 'Gaussian Filter']


''' --------------------------------------------------- MAIN ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
def main():

    threadQueue = Queue.Queue()
    
    negotiatorServerThread = myPeerServerThread(threadQueue)
    negotiatorServerThread.start()

    negotiatorServerThread.join()

if __name__ == '__main__':
    main()
