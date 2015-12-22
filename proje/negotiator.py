
__author__ = 'sumeyye'

from pyGraphics_ui import Ui_ImageProcessor
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import numpy as np
import math
import threading
import socket
import Queue
import time
import copy


''' ------------------------------------------- NEGOTIATOR CLIENT THREAD ---------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# HELLO => SALUT <type>
# CLOSE => BUBYE
# Arabulucu-istemcinin isi sadece eslerin sunucularını test etmek
class myNegotiatorClientThread (threading.Thread):
    def __init__(self, threadID, peerSocket, peerAddr, workQueue, processedQueue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.peerSocket = peerSocket
        self.peerAddr = peerAddr
        self.workQueue = workQueue
        self.processedQueue = processedQueue

     def run(self):
        global CONNECT_POINT_LIST
        value = CONNECT_POINT_LIST.get(self.peerAddr)
        try:
            pointTime = str.split(value, ":")[1] #N-W:123456 ornegin, zamani(123456) aliyoruz
            currentTime = time.time()
            # simdiki zaman x ise ve en son x-10 da cevap vermisse, tekrar hello diyoruz.
            if ((currentTime - pointTime) == 600):
                self.peerSocket.send("HELLO")
                try:
                    response = self.peerSocket.recv(buff)
                    # SALUT'den baska bir cevap gelmisse eger
                    # CMDER yolluyoruz, connection'i kapatip listeden dusuruyoruz.
                    if response != "SALUT":
                        self.peerSocket.send("CMDER")
                        self.peerSocket.close()
                        # Listede hala var gorunuyorsa, listeden dusuruyoruz.
                        if self.peerAddr in CONNECT_POINT_LIST:
                            del CONNECT_POINT_LIST[self.peerAddr]
                    # Eger SALUT cevabi gelmisse, last seen'ini update ediyoruz.k
                    else:
                        #Statu'sunu S yapip, time'ini guncelliyoruz.
                        CONNECT_POINT_LIST[self.peerAddr] = value[:2] + "S:" + currentTime
                except socket.timeout:
                    self.peerSocket.close()
            # son 10 dakkadan uzun bir suredir cevap gelmemisse, close diyoruz.
            elif ((currentTime - pointTime) > 600):
                self.peerSocket.send("CLOSE")
                try:
                    response = self.peerSocket.recv(buff)
                    # BUBYE'den baska bir cevap gelmisse eger
                    # CMDER yolluyoruz
                    if response != "BUBYE":
                        self.peerSocket.send("CMDER")
                    self.peerSocket.close()
                    # Listede hala var gorunuyorsa, listeden dusuruyoruz.
                    if self.peerAddr in CONNECT_POINT_LIST:
                        del CONNECT_POINT_LIST[self.peerAddr]
                except socket.timeout:
                    self.peerSocket.close()
        except socket.timeout:
            self.peerSocket.close()


#buffer buyuklugu
buff = 12345
# Baglanti listesi
CONNECT_POINT_LIST = {} #{[addr1,type1-S:time1],[addr2,type2-W:time2],...}
#thread listesi
threads = []
# kilit mekanizmasi
pLock = threading.Lock()
#thread sayisi
threadCounter = 0

s = socket.socket()             # socket yaratiyoruz
host = socket.gethostname()     # sunucunun adresi
port = 10000                    # dinleyecegi port numarasi
s.bind((host, port))            # bind islemi gerceklestirilir
s.listen(5)                     # sunucu portu dinlemeye baslar(baglanti kuyrugunda tutulacak baglanti sayisi : 5)

while True:

    c, addr = s.accept()
    workQueue = Queue.Queue()
    processedQueue = Queue.Queue()

    threadCounter += 1
    negotiatorClientThread = myNegotiatorClientThread(c, addr, CONNECT_POINT_LIST, workQueue, processedQueue)
    threads.append(negotiatorClientThread)
    negotiatorClientThread.start()

    app = imGui(workQueue,processedQueue, pLock)
    app.run()

for a in range(0,threadCounter):
    workQueue.put("END")

for thread in threads:
    thread.join()
