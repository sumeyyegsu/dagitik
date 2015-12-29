__author__ = 'sumeyye'

import threading
import socket
import Queue
import time
import copy

''' --------------------------------------- NEGOTIATOR CLIENT THREAD -------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Bu threadin gorevi: Negotiator'in calistigi sure boyunca, UPDATE_INTERVAL araliginda, tum baglantilari kontrol
# edip CONNECTION_POINT_LIST'i guncellemek.
# Arabulucu - istemci tarafinda calisan thread:
class myNegotiatorClientThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        logQueue.put("C_NEGOTIATOR:  myNegotiatorClientThread yaratildi.")
        while True:
            time.sleep(UPDATE_INTERVAL)
            for peerAddr in CONNECT_POINT_LIST.keys():
                testPeerConnectionThread = myTestPeerConnectionThread(peerAddr)
                testPeerConnectionThread.start()
            logQueue.put("C_NEGOTIATOR: " + "CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))

''' ---------------------------------------- TEST PEER CONNECTION THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Ip/Port ikilisine gore, test edilecek peer/negotiator icin yaratilan threaddir.
# Baglantiyi test edip ona gore, CONNECT_POIN_LIST'i guncelliyor.
# Baglantiyi test eden thread:
class myTestPeerConnectionThread(threading.Thread):
    def __init__(self, peerAddr):
        threading.Thread.__init__(self)
        self.peerAddr = peerAddr
        self.peerHost = str(self.peerAddr[0])
        self.peerPort = int(self.peerAddr[1])

    def run(self):
        global CONNECT_POINT_LIST
        logQueue.put("C_NEGOTIATOR: myTestPeerConnectionThread yaratildi.")
        s = socket.socket() 
        s.settimeout(int(UPDATE_INTERVAL/5))
        temporaryList = CONNECT_POINT_LIST.copy() 
        try:
            s.connect((self.peerHost, self.peerPort))
            logQueue.put("C_NEGOTIATOR: (" + self.peerHost + ", " + str(self.peerPort) + ") ile baglanti kuruldu.")

            s.send("HELLO")
            logQueue.put("C_NEGOTIATOR: HELLO gonderildi.")
            try:
                response1 = s.recv(buff)
                logQueue.put("C_NEGOTIATOR: Gonderilen HELLO'ya alinan cevap: " + str(response1))
                if response1[:5] != "SALUT":
                    s.send("CMDER")
                    logQueue.put("C_NEGOTIATOR: CMDER gonderildi.")
                    if self.peerAddr in temporaryList.keys():
                        logQueue.put("C_NEGOTIATOR: Peer listeden siliniyor.")
                        CONNECT_POINT_LIST.pop(self.peerAddr)
                else:
                    value = temporaryList[self.peerAddr]
                    CONNECT_POINT_LIST[self.peerAddr] = "S:" + time.time()
                s.close()
                logQueue.put("C_NEGOTIATOR: Peer baglantisini kapatti.")
            except socket.timeout:
                logQueue.put("C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor. Peer listeden siliniyor.")
                temporaryList.pop(self.peerAddr)
                s.close()
            
            s.send("CLOSE")
            logQueue.put("C_NEGOTIATOR: CLOSE gonderiliyor.")
            try:
                response2 = s.recv(buff)
                logQueue.put("C_NEGOTIATOR: Gonderilen CLOSE'a alinan cevap: " + str(response2))
                if response2[:5] != "BUBYE":
                    s.send("CMDER")
                    logQueue.put("C_NEGOTIATOR: Peer'a CMDER gonderildi.")
                    if self.peerAddr in temporaryList.keys():
                        logQueue.put("C_NEGOTIATOR: Peer listeden siliniyor.")
                        temporaryList.pop(self.peerAddr)
            except socket.timeout:
                logQueue.put("C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor. Peer listeden siliniyor.")
                temporaryList.pop(self.peerAddr)
                s.close()
            
        except :
            logQueue.put("C_NEGOTIATOR: Bir sorun olustu. Baglanti kapatiliyor. Peer listeden siliniyor.")
            temporaryList.pop(self.peerAddr)
            s.close()
        CONNECT_POINT_LIST = copy.deepcopy(temporaryList)
        

''' -----------------------------------NEGOTIATOR SERVER THREAD-------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Arabulucu - sunucu tarafi:
class myNegotiatorServerThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.port = 10000               # dinleyecegi port numarasi
        self.host = "127.0.0.5"         # sunucunun adresi
    def run(self):
        logQueue.put("S_NEGOTIATOR:  myNegotiatorServerThread yaratildi.")
        s = socket.socket()             # socket yaratiyoruz
        logQueue.put("S_NEGOTIATOR: Soket yaratildi.")
        s.bind((self.host, self.port))  # bind islemi gerceklestirilir
        s.listen(4)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)
        while True:
            c,addr = s.accept()
            logQueue.put("S_NEGOTIATOR: " + str(addr)  + "'den/dan baglanti geldi.")
            logQueue.put("S_NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))
            negotiatorServerReceiveThread = myNegotiatorServerReceiveThread(c, addr)
            negotiatorServerReceiveThread.start()
        
''' -------------------------------------- NEGOTIATOR SERVER RECEIVE THREAD ------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''

class myNegotiatorServerReceiveThread(threading.Thread):
    def __init__(self, peerSocket, peerAddr):
        threading.Thread.__init__(self)
        self.peerSocket = peerSocket
        self.peerAddr = peerAddr
        self.flagRegistration = False

    def run(self):
        global CONNECT_POINT_LIST
        logQueue.put("S_NEGOTIATOR: myNegotiatorServerReceiveThread Yaratildi.")
        while True:
            try:
                receivedData = self.peerSocket.recv(buff)
                if receivedData:
                    logQueue.put("S_NEGOTIATOR: Alinan veri: " + receivedData)
                    self.parser(receivedData)
            except socket.timeout:
                self.peerSocket.close()
                break
        logQueue.put("S_NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))

    def parser(self, receivedData):
        logQueue.put("S_NEGOTIATOR: Parser calisiyor. Alinan data: " + receivedData)
        receivedData = receivedData.strip()

        if (receivedData[:5] == "HELLO"):
            logQueue.put("S_NEGOTIATOR: SALUT gonderiliyor.")
            self.peerSocket.send("SALUT")

        elif (receivedData[:5] == "CLOSE"):
            logQueue.put("S_NEGOTIATOR: BUBYE gonderiliyor.")
            self.peerSocket.send("BUBYE")
            if self.peerAddr in CONNECT_POINT_LIST.keys():
                logQueue.put("S_NEGOTIATOR: Peer listeden silinir.")
                CONNECT_POINT_LIST.pop(self.peerAddr)
                logQueue.put("S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))

        elif (receivedData[:5] == "REGME"):
            host, port = str.split(receivedData[6:], ':', 1)
            port = int(port)
            if (host, port) in CONNECT_POINT_LIST.keys():
                logQueue.put("S_PEER: Baglanti zaten listede kayitli. Status'u S yapiliyor. Time'i guncelleniyor.")
                value = "S:" + str(time.time())
                CONNECT_POINT_LIST[(host, port)] = value
                print "S_PEER: " + "REGOK " + str(value[2:]) + " gonderilir."
                self.peerSocket.send("REGOK " + str(value[2:]))
                logQueue.put("S_PEER: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))
            else:
                logQueue.put("S_NEGOTIATOR: REGWA gonderildi.")
                self.peerSocket.send("REGWA")
                logQueue.put("S_NEGOTIATOR: Baglanti listeye ekleniyor. Status'u W yapiliyor. Time'i guncelleniyor.")
                CONNECT_POINT_LIST[(host, port)] = "W:" + str(time.time())
                logQueue.put("S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))

        elif (receivedData[:5] == "GETNL"):
            if self.flagRegistration:
                nlsize = int(receivedData[6:])
                if nlsize == 0:
                    nlsize = 50 #nlsize tanimlanmadigi yerde 50 kabul edilir.
                self.peerSocket.send("NLIST BEGIN\n")
                logQueue.put("S_NEGOTIATOR: Baglanti uzerinden gonderilen: NLIST BEGIN\n")
                i = 0
                for key, value in CONNECT_POINT_LIST.iterkeys():
                    if i <= nlsize:
                        data = str(key[0]) + ":" + str(key[1]) + ":"\
                                + str(value[0]) + ":" + str(value[2:]) + "\n"
                        self.peerSocket.send(data)
                        logQueue.put("S_NEGOTIATOR: Baglanti uzerinden gonderilen data: " + data)
                        i += 1
                self.peerSocket.send("NLIST END")
                logQueue.put("S_NEGOTIATOR: Baglanti uzerinden gonderilen data : NLIST END")
                logQueue.put("S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST))
            else:
                logQueue.put("REGER gonderiliyor.")
                self.peerSocket.send("REGER")
        else:
            logQueue.put("S_NEGOTIATOR: CMDER gonderiliyor.")
            self.peerSocket.send("CMDER")
        logQueue.put("S_NEGOTIATOR: Baglanti kapatiliyor.")
        self.peerSocket.close()

    
'''--------------------------------------------- LOG THREAD -----------------------------------------------------'''
''' ------------------------------------------------------------------------------------------------------------- '''
# (print'le konsola bastiklarimi bir log dosyasinda tutmayi tercih ettim.)
class myLogThread (threading.Thread):
    def __init__(self, logFileName):
        threading.Thread.__init__(self)
        self.fid = open(logFileName, "a")
    def log(self, message):
        self.fid.write(str(time.ctime()) + " - " + message)
        self.fid.flush()
    def run(self):
        while True:
            if not logQueue.empty():
                self.log(str(logQueue.get()) + "\n")
        self.fid.close()


#buffer buyuklugu
buff = 2048
# Baglanti listesi
CONNECT_POINT_LIST = {} #{[addr1,type1-S:time1],[addr2,type2-W:time2],...} yani KEY = (host,port) ve VALUE = type-status:time
# CONNECT_POINT_LIST'in bir sonraki guncellemesinden onceki bekleme suresi
UPDATE_INTERVAL = 20
# kilit mekanizmasi
pLock = threading.Lock()
# log dosyasi icin olusturulan kuyruk
logQueue = Queue.Queue()

''' --------------------------------------------------- MAIN ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
def main():

    logThread = myLogThread("log.txt")
    logThread.start()

    negotiatorClientThread = myNegotiatorClientThread()
    negotiatorClientThread.start()

    negotiatorServerThread = myNegotiatorServerThread()
    negotiatorServerThread.start()

    negotiatorClientThread.join()
    negotiatorServerThread.join()

if __name__ == '__main__':
    main()
