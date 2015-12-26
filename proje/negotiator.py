__author__ = 'sumeyye'

import threading
import socket
import Queue
import time
import copy

# TODO: timeout ile ilgilenme.
# TODO: <type> hakkinda tekrar dusunme. Gereksiz olabilir, gereksizse sistemden type bilgisini cikarma.

''' ---------------------------------------- TEST PEER CONNECTION THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Ip/Port ikilisine gore, test edilecek birim icin yaratilan thread.
# Baglantiyi test edip ona gore, CONNECT_POIN_LIST'i guncelliyor.
class myTestPeerConnectionThread(threading.Thread):
    def __init__(self, peerAddr):
        threading.Thread.__init__(self)
        self.peerAddr = peerAddr

    def run(self):
        global CONNECT_POINT_LIST
        print "C_NEGOTIATOR: myTestPeerConnectionThread Yaratildi."
        s = socket.socket() #baglanti testi icin soket aciyoruz
        temporaryList = CONNECT_POINT_LIST.copy() #listenin bir kopyasini temporaryList'e atiyoruz.
        try:
            s.connect(CONNECT_POINT_LIST[self.peerAddr][0], CONNECT_POINT_LIST[self.peerAddr][1]) #ip,port a baglaniyoruz.
            s.send("HELLO")
            print "C_NEGOTIATOR: HELLO gonderildi."
            try:
                response1 = s.recv(buff)
                print "C_NEGOTIATOR: Gonderilen HELLO'ya alinan cevap: " + str(response)
                # SALUT'den baska bir cevap gelmisse eger
                # CMDER yolluyoruz, connection'i kapatip listeden dusuruyoruz.
                if response1 != "SALUT":
                    print "C_NEGOTIATOR: HELLO'ya gelen cevap SALUT'den farklidir."
                    s.send("CMDER")
                    print "C_NEGOTIATOR: Peer'a CMDER gonderildi."
                    # Listede hala var gorunuyorsa, listeden dusuruyoruz.
                    if self.peerAddr in temporaryList.keys():
                        print "C_NEGOTIATOR: HELLO'ya karsilik SALUT'den baska bir cevap yollayan peer, listeden silinir."
                        del CONNECT_POINT_LIST[self.peerAddr]
                        print "C_NEGOTIATOR: Yeni temporaryList: " + str(temporaryList)
                # Eger SALUT cevabi gelmisse, last seen'ini update ediyoruz.
                else:
                    print "C_NEGOTIATOR: HELLO'ya gelen cevap SALUT'dur."
                    value = temporaryList[self.peerAddr]
                    # Statu'sunu S yapip, time'ini guncelliyoruz.
                    CONNECT_POINT_LIST[self.peerAddr] = value[0] + "-S:" + time.time()
                    print "C_NEGOTIATOR: Yeni temporaryList: " + str(temporaryList)
                s.close()
                print "C_NEGOTIATOR: Peer baglantisini kapatti."
            except socket.timeout:
                print "C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor. Peer listeden siliniyor."
                del temporaryList[self.peerAddr]
                print "C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor."
                s.close()
            
            s.send("CLOSE")
            print "C_NEGOTIATOR: CLOSE gonderiliyor."
            try:
                response2 = s.recv(buff)
                print "C_NEGOTIATOR: Gonderilen CLOSE'a alinan cevap: " + str(response2)
                # BUBYE'den baska bir cevap gelmisse eger
                # CMDER yolluyoruz
                if response2 != "BUBYE":
                    print "C_NEGOTIATOR: CLOSE'a gelen cevap BUBYE'den farklidir."
                    s.send("CMDER")
                    print "C_NEGOTIATOR: Peer'a CMDER gonderildi."
                    if self.peerAddr in temporaryList.keys():
                        print "C_NEGOTIATOR: CLOSE'a karsilik BUBYE'dan baska bir cevap yollayan peer listeden silinir."
                        del temporaryList[self.peerAddr]
                        print "C_NEGOTIATOR: Yeni temporaryList: " + str(temporaryList)
            except socket.timeout:
                print "C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor. Peer listeden siliniyor."
                del temporaryList[self.peerAddr]
                print "C_NEGOTIATOR: Yeni temporaryList: " + str(temporaryList)
                s.close()
            
        except :
            print "C_NEGOTIATOR: Bir sorun olustu. Baglanti kapatiliyor. Peer listeden siliniyor."
            del temporaryList[self.peerAddr]
            print "C_NEGOTIATOR: Yeni temporaryList: " + str(temporaryList)
            s.close()
        CONNECT_POINT_LIST = copy.deepcopy(temporaryList)
        
''' --------------------------------------- NEGOTIATOR CLIENT THREAD ------------------------------------------- '''
# Bu threadin gorevi: Negotiator-Client calistigi sure boyunca, UPDATE_INTERVAL araliginda, tum baglantilari kontrol
# edip CONNECTION_POINT_LIST'i guncellenmeye calisilirken, her baglantiyi tek tek kontrol etmek.
class myNegotiatorClientThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "C_NEGOTIATOR:  myNegotiatorClientThread Yaratildi."
        while True:
            time.sleep(UPDATE_INTERVAL)
            for peerAddr in CONNECT_POINT_LIST.keys():
                testPeerConnectionThread = myTestPeerConnectionThread(peerAddr)
                testPeerConnectionThread.start()
            print "C_NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)

        
''' ------------------------------------------- NEGOTIATOR SERVER THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''


# HELLO => SALUT <type>
# CLOSE => BUBYE
# REGME <ip>:<port> => REGWA | REGOK <time> | REGER
# GETNL <nlsize> => NLIST BEGIN
#                   <ip>:<port>:<time>:<type>
#                   <ip>:<port>:<time>:<type>
#                   ...
#                   NLIST END
#Es-istemcilerinin arabulucu sunucudan beklentileri diger eslerin baglantı bilgileridir.

class myNegotiatorServerThread(threading.Thread):
    def __init__(self, threadID, peerSocket, peerAddr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.peerSocket = peerSocket
        self.peerAddr = peerAddr

    def run(self):
        print "S_NEGOTIATOR: Server Thread Yaratildi."
        print "S_NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
        while True:
            try:
                receivedData = self.peerSocket.recv(buff)
                print "S_NEGOTIATOR: Alinan veri: " + receivedData
                self.parser(receivedData)
            except socket.error:
                self.peerSocket.close()
                break

    def parser(self, receivedData):
        print "S_NEGOTIATOR: parser calisiyor. Alinan data: " + receivedData
        receivedData = receivedData.strip()
        # herhangi bir uc'tan HELLO gelirse SALUT cevabini yolluyoruz.
        if (receivedData == "HELLO"):
            print "S_NEGOTIATOR: Alinan veri HELLO -> SALUT cevabi gonderiliyor."
            self.peerSocket.send("SALUT")

        # herhangi bir birimden CLOSE gelirse, BUBYE deyip baglantimizi kapatiyoruz.
        elif (receivedData == "CLOSE"):
            print "S_NEGOTIATOR: Alinan veri CLOSE -> BUBYE cevabi gonderiliyor."
            self.peerSocket.send("BUBYE")
            print "S_NEGOTIATOR: Baglanti kapatiliyor."
            self.peerSocket.close()
            if self.peerAddr in CONNECT_POINT_LIST.keys():
                print "S_NEGOTIATOR: Peer listeden silinir."
                del CONNECT_POINT_LIST[self.peerAddr]
                print "S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)

        # REGME komutu geldiyse
        elif (receivedData == "REGME"):
            try:
                print "S_NEGOTIATOR: REGME istegi geldi." \
                        "Bilirim guldurmez devr-i alemde," \
                        "Bir gunumu yuz bin zara yazmislar..."
                host, port = str.split(receivedData[6:], ':', 1)
                print "S_NEGOTIATOR: Alinan veri: " + receivedData
                value = CONNECT_POINT_LIST[host + port]
                # peer listede zaten varsa
                if host + port in CONNECT_POINT_LIST.keys():  # ex: N-S:123213546
                    print "S_NEGOTIATOR: " + host + port + " listede zaten varsa status'u S yapilir."
                    if value[2] == "S":
                        value[3:] = ":" + str(time.time())
                        print "S_NEGOTIATOR: " + "REGOK " + str(value[4:]) + " gonderilir."
                        self.peerSocket.send("REGOK " + str(value[4:]))
                    print "S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
                # peer listede yoksa
                else:
                    print "S_NEGOTIATOR: " + host + port + " listede yoksa, status'u W ile eklenir."
                    # kaydi beklemeye aliyoruz
                    print "S_NEGOTIATOR: REGWA gonderildi."
                    self.peerSocket.send("REGWA")
                    CONNECT_POINT_LIST[host + port] = "?-W:" + str(time.time())  ##P mi N mi neye gore ekleyecegiz???
                    print "S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
                    print "S_NEGOTIATOR: Baglanti kapatiliyor."
                    self.peerSocket.close()
            except:
                self.peerSocket.send("REGER")
                print "S_NEGOTIATOR: REGER gonderildi. - Baglanti kapatiliyor."
                self.peerSocket.close()


        # REGWA komutu geldiyse ??tekrar bakicalacak
        elif (receivedData == "REGWA"):
            host, port = str.split(receivedData[6:], ':', 1)
            value = CONNECT_POINT_LIST[host + port]
            print "S_NEGOTIATOR: REGWA geldi hos geldi. Leylim leeeeey."
            # time'i guncelliyoruz (P-W:123132) (gonderen peer'in)
            CONNECT_POINT_LIST[self.peerAddr] = value[:4] + str(time.time())
            print "S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
            # eksik ???????


        # GETNL : negotiator'in listesi istendiyse
        elif (receivedData == "GETNL"):
            nlsize = int(receivedData[6:])
            print "S_NEGOTIATOR: GETNL geldi. nlsize: " + str(nlsize)
            self.peerSocket.send("NLIST BEGIN\n")
            print "S_NEGOTIATOR: Baglanti uzerinden gonderilen: NLIST BEGIN\n"
            i = 0
            for key, value in CONNECT_POINT_LIST.iterkeys():
                if i <= nlsize:
                    data = str(key[0]) + ":" + str(key[1]) + ":"\
                            + str(value[0]) + ":" + str(value[4:]) + "\n"
                    self.peerSocket.send(data)
                    print "S_NEGOTIATOR: Baglanti uzerinden gonderilen: " + data
                    i += 1
            self.peerSocket.send("NLIST END")
            print "S_NEGOTIATOR: Baglanti uzerinden gonderilen: NLIST END"
            print "S_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)

    
#buffer buyuklugu
buff = 2048
# Baglanti listesi
CONNECT_POINT_LIST = {} #{[addr1,type1-S:time1],[addr2,type2-W:time2],...}
# CONNECT_POINT_LIST'in bir sonraki guncellemesinden onceki bekleme suresi
UPDATE_INTERVAL = 60
# kilit mekanizmasi
pLock = threading.Lock()

s = socket.socket()             # socket yaratiyoruz
print "NEGOTIATOR: Socket created."
host = socket.gethostname()     # sunucunun adresi
port = 10000                    # dinleyecegi port numarasi
s.bind((host, port))            # bind islemi gerceklestirilir
s.listen(5)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)

''' --------------------------------------------------- MAIN ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
def main():

    threadQueue = Queue.Queue()

    c, addr = s.accept()
    print "NEGOTIATOR: Got a connection from " + str(addr)
    print "NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)

    negotiatorClientThread = myNegotiatorClientThread(c, addr, CONNECT_POINT_LIST, threadQueue)
    negotiatorClientThread.start()

    negotiatorServerThread = myNegotiatorServerThread(c, addr, CONNECT_POINT_LIST, threadQueue)
    negotiatorServerThread.start()

    negotiatorClientThread.join()
    negotiatorServerThread.join()

