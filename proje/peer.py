__author__ = 'sumeyye'

import threading
import socket
import time
import copy
from time import strftime

''' --------------------------------------- PEER CLIENT THREAD -------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Es istemci tarafi
class myPeerClientThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.negotiatorSocket = socket.socket()
    def run(self):
        try:
            self.negotiatorSocket.connect((negotiatorHost, negotiatorPort))
            self.negotiatorSocket.send("REGME " + myHost + ":" + str(myPort))
            testConnectionList = myTestConnectionListThread()
            testConnectionList.start()
            testConnectionList.join()
        except:
            self.negotiatorSocket.close()


''' --------------------------------------- TEST CONNECTION LIST THREAD -------------------------------------------- '''
''' ---------------------------------------------------------------------------------------------------------------- '''
# Hem kendi listesindeki tum baglantilari testConnectionThread ile test ediyor
# Hem de tum test ettigi baglantilarin baglanti listelerinden kendi listesini guncelliyor.
class myTestConnectionListThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "C_PEER:  myTestConnectionListThread yaratildi."
        while True:
            time.sleep(UPDATE_INTERVAL)
            for peerAddr in CONNECT_POINT_LIST.keys():
                testConnectionThread = myTestConnectionThread(peerAddr)
                testConnectionThread.start()
                getListFromConnection = myGetListFromConnectionThread(peerAddr)
                getListFromConnection.start()
                testConnectionThread.join()
                getListFromConnection.join()
            print "C_PEER: " + strftime("%m/%d/%Y %H:%M:%S") + " | CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)

''' ------------------------------------ GET LIST FROM CONNECTION THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
#Baglanti listesindeki tum baglantilarin baglanti listelerini alip, kendi baglanti listesini guncelliyor.
class myGetListFromConnectionThread (threading.Thread):
    def __init__(self, peerAddr):
        threading.Thread.__init__(self)
        self.peerAddr = peerAddr
        self.host = peerAddr[0]
        self.port = peerAddr[1]
        self.peerSocket = socket.socket()
    def run(self):
        print "C_PEER: myGetListFromConnectionThread yaratildi."
        self.peerSocket.connect((self.host, int(self.port)))
        self.peerSocket.send("REGME " + self.host + ":" + self.port)
        response = self.peerSocket.recv(buff)
        if response[:5] == "REGOK":
            self.peerSocket.send("GETNL")
            receivedData = self.peerSocket.recv(buff)
            if receivedData == "NLIST BEGIN":
                receivedData = self.peerSocket.recv(buff)
                while receivedData != "NLIST END":
                    ligne = str.split(receivedData, '\n')
                    ligneHost, lignePort, ligneType, ligneTime= str.split(ligne, ":", 3)
                    lignePort = int(lignePort)
                    if (ligneHost, lignePort) not in CONNECT_POINT_LIST:
                        CONNECT_POINT_LIST[(ligneHost, lignePort)]= "S:" + ligneTime
            # listede sonuna ulasilmadan baska bir yapi gonderilirse istemci baglantiyi kapatir.
            self.peerSocket.close()

''' ---------------------------------------- TEST CONNECTION THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Kendi baglanti listesindeki baglantilari test ediyor.
class myTestPeerConnectionThread(threading.Thread):
    def __init__(self, peerAddr):
        threading.Thread.__init__(self)
        self.peerAddr = peerAddr
        self.peerHost = self.peerAddr[0]
        self.peerPort = self.peerAddr[1]

    def run(self):
        global CONNECT_POINT_LIST
        print "C_PEER: myTestPeerConnectionThread yaratildi."
        s = socket.socket() 
        s.settimeout(int(UPDATE_INTERVAL/5))
        temporaryList = CONNECT_POINT_LIST.copy() 
        try:
            s.connect((self.peerHost, self.peerPort))
            print "C_PEER: (" + self.peerHost + ", " + str(self.peerPort) + ") ile baglanti kuruldu."

            s.send("HELLO")
            print "C_PEER: HELLO gonderildi."
            try:
                response1 = s.recv(buff)
                print "C_PEER: Gonderilen HELLO'ya alinan cevap: " + str(response1)
                if response1[:5] != "SALUT":
                    s.send("CMDER")
                    print "C_PEER: CMDER gonderildi."
                    if self.peerAddr in temporaryList.keys():
                        print "C_PEER: Peer listeden siliniyor."
                        CONNECT_POINT_LIST.pop(self.peerAddr)
                else:
                    value = temporaryList[self.peerAddr]
                    CONNECT_POINT_LIST[self.peerAddr] = "S:" + time.time()
                s.close()
                print "C_PEER: Peer baglantisini kapatti."
            except socket.timeout:
                print "C_PEER: Zaman asimi. Baglanti kapatiliyor. Peer listeden siliniyor."
                temporaryList.pop(self.peerAddr)
                s.close()
            
            s.send("CLOSE")
            print "C_PEER: CLOSE gonderiliyor."
            try:
                response2 = s.recv(buff)
                print "C_PEER: Gonderilen CLOSE'a alinan cevap: " + str(response2)
                if response2[:5] != "BUBYE":
                    s.send("CMDER")
                    print "C_PEER: Peer'a CMDER gonderildi."
                    if self.peerAddr in temporaryList.keys():
                        print "C_PEER: Peer listeden siliniyor."
                        temporaryList.pop(self.peerAddr)
            except socket.timeout:
                print "C_PEER: Zaman asimi. Baglanti kapatiliyor. Peer listeden siliniyor."
                temporaryList.pop(self.peerAddr)
                s.close()
            
        except :
            print "C_PEER: Bir sorun olustu. Baglanti kapatiliyor. Peer listeden siliniyor."
            temporaryList.pop(self.peerAddr)
            s.close()
        CONNECT_POINT_LIST = copy.deepcopy(temporaryList)
        

''' ----------------------------------------PEER SERVER THREAD-------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Es - sunucu tarafi
class myPeerServerThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.myPeerSocket = socket.socket()
    def run(self):
        self.myPeerSocket.bind((myHost, myPort))
        self.myPeerSocket.listen(4)               
        while True:
            c, ddr = self.myPeerSocket.accept()
            peerServerReceiveThread = myPeerServerReceiveThread(c, addr)
            peerServerReceiveThread.start()
            peerServerReceiveThread.join()

''' -------------------------------------- PEER SERVER RECEIVE THREAD ------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''

class myNegotiatorServerReceiveThread(threading.Thread):
    def __init__(self, peerSocket, peerAddr):
        threading.Thread.__init__(self)
        self.peerSocket = peerSocket
        self.peerAddr = peerAddr
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
                print "..."
            else:
                self.peerSocket.send("REGER")
                
        # PATCH 
        elif (receivedData[:5] == "PATCH"):
            if self.flagRegistration:
                print "..."
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
CONNECT_POINT_LIST = {} #{[addr1,S:time1],[addr2,W:time2],...} yani KEY = (host,port) ve VALUE = status:time
# CONNECT_POINT_LIST'in bir sonraki guncellemesinden onceki bekleme suresi
UPDATE_INTERVAL = 20
# kilit mekanizmasi
pLock = threading.Lock()
# peer'in sahip oldugu fonksiyonlarin listesi
functionList = ['Gray Scale Filter', 'Sobel Filter', 'Binarize Filter', 'Prewitt Filter', 'Gaussian Filter']
#Peer'in host'u
myHost = "127.0.0.5"
#Peer'in port'u
myPort = 10000
#Negotiator'in host'u
negotiatorHost = "127.0.0.6"
#Negotiator'in port'u
negotiatorPort = 10001

''' --------------------------------------------------- MAIN ---------------------------------------------------- '''
''' -------------------------------------------------------------------------------------------------------------- '''
def main():
    
    peerClientThread = myPeerClientThread()
    peerClientThread.start()

    peerServerThread = myPeerServerThread()
    peerServerThread.start()

    peerClientThread.join()
    peerServerThread.join()

if __name__ == '__main__':
    main()
