__author__ = 'sumeyye'

import threading
import socket
import Queue
import time

''' ------------------------------------------- NEGOTIATOR CLIENT THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''


# HELLO => SALUT <type>
# CLOSE => BUBYE
# Arabulucu-istemcinin isi sadece eslerin sunucularını test etmek
class myNegotiatorClientThread (threading.Thread):
    def __init__(self, threadID, peerSocket, peerAddr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.peerSocket = peerSocket
        self.peerAddr = 

    def run(self):
        print "C_NEGOTIATOR: Client Thread Yaratildi."
        if self.peerAddr in CONNECT_POINT_LIST.keys():
        	print "C_NEGOTIATOR: Bu peer listede zaten kayitli."
		try:
            		value = CONNECT_POINT_LIST[self.peerAddr]
                	print "C_NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
                	pointTime = str.split(value, ":")[1]  # N-W:123456 ornegin, zamani(123456) aliyoruz
                	# simdiki zaman x ise ve en son x-UPDATE_INTERVAL da cevap vermisse
            		if ((time.time() - pointTime) == UPDATE_INTERVAL):
                		self.peerSocket.send("HELLO")
                		print "C_NEGOTIATOR: HELLO gonderildi."
                		try:
                    			response = self.peerSocket.recv(buff)
                    			print "C_NEGOTIATOR: Gonderilen HELLO'ya alinan cevap: " + str(response)
                    			# SALUT'den baska bir cevap gelmisse eger
                    			# CMDER yolluyoruz, connection'i kapatip listeden dusuruyoruz.
                    			if response != "SALUT":
                    				print "C_NEGOTIATOR: HELLO'ya gelen cevap SALUT'den farklidir."
                        			self.peerSocket.send("CMDER")
                        			print "C_NEGOTIATOR: Peer'a CMDER gonderildi."
                        			self.peerSocket.close()
                        			print "C_NEGOTIATOR: Peer baglantisini kapatti."
                        			# Listede hala var gorunuyorsa, listeden dusuruyoruz.
                        			if self.peerAddr in CONNECT_POINT_LIST.keys():
                            				print "C_NEGOTIATOR: HELLO'ya karsilik SALUT'den baska bir cevap yollayan peer, listeden silinir."
                                			del CONNECT_POINT_LIST[self.peerAddr]
                                			print "C_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
                    			# Eger SALUT cevabi gelmisse, last seen'ini update ediyoruz.
                    			else:
                    				print "C_NEGOTIATOR: HELLO'ya gelen cevap SALUT'dur."
                        			#Statu'sunu S yapip, time'ini guncelliyoruz.
                        			CONNECT_POINT_LIST[self.peerAddr] = value[0] + "-S:" + time.time()
               					print "C_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
                		except socket.timeout:
                			print "C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor."
                    			self.peerSocket.close()
            		# son UPDATE_INTERVAL'dan uzun bir suredir cevap gelmemisse, close diyoruz.
            		elif ((time.time() - pointTime) > UPDATE_INTERVAL):
            			print "C_NEGOTIATOR: Beklenen zaman araliginda peer'dan cevap gelmedi."
                		self.peerSocket.send("CLOSE")
                		try:
                    			response = self.peerSocket.recv(buff)
                    			print "C_NEGOTIATOR: Gonderilen CLOSE'a alinan cevap: " + str(response)
                    			# BUBYE'den baska bir cevap gelmisse eger
                    			# CMDER yolluyoruz
                    			if response != "BUBYE":
                    				print "C_NEGOTIATOR: CLOSE'a gelen cevap BUBYE'den farklidir."
                            			self.peerSocket.send("CMDER")
                            			print "C_NEGOTIATOR: Peer'a CMDER gonderildi.
                    			self.peerSocket.close()
                    			print "C_NEGOTIATOR: Peer baglantisini kapatti."
                    			# Listede hala var gorunuyorsa, listeden dusuruyoruz.
                    			if self.peerAddr in CONNECT_POINT_LIST.keys():
                    				print "C_NEGOTIATOR: Peer listeden silinir."
                        			del CONNECT_POINT_LIST[self.peerAddr]
                        			print "C_NEGOTIATOR: Yeni CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)
        			except socket.timeout:
        				print "C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor."
                    			self.peerSocket.close()
                except socket.timeout:
                	print "C_NEGOTIATOR: Zaman asimi. Baglanti kapatiliyor."
                	self.peerSocket.close()

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
                	self.clientSocket.close()
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
                	print "S_NEGOTIATOR: REGME istegi geldi."
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
buff = 12345
# Baglanti listesi
CONNECT_POINT_LIST = {} #{[addr1,type1-S:time1],[addr2,type2-W:time2],...}
# CONNECT_POINT_LIST'in bir sonraki guncellemesinden onceki bekleme suresi
UPDATE_INTERVAL = 60
#thread listesi
threads = []
# kilit mekanizmasi
pLock = threading.Lock()
#thread sayisi
threadCounter = 0

s = socket.socket()             # socket yaratiyoruz
print "NEGOTIATOR: Socket created."
host = socket.gethostname()     # sunucunun adresi
port = 10000                    # dinleyecegi port numarasi
s.bind((host, port))            # bind islemi gerceklestirilir
s.listen(5)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)

while True:

    c, addr = s.accept()
    print "NEGOTIATOR: Got a connection from " + str(addr)
    print "NEGOTIATOR: CONNECT_POINT_LIST: " + str(CONNECT_POINT_LIST)

    workQueue = Queue.Queue()
    processedQueue = Queue.Queue()

    threadCounter += 1
    negotiatorClientThread = myNegotiatorClientThread(c, addr, CONNECT_POINT_LIST)
    threads.append(negotiatorClientThread)
    negotiatorClientThread.start()

    threadCounter += 1
    negotiatorServerThread = myNegotiatorServerThread(c, addr, CONNECT_POINT_LIST)
    threads.append(negotiatorServerThread)
    negotiatorServerThread.start()

for thread in threads:
    thread.join()
