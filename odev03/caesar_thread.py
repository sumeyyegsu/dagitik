__author__ = 'sumeyye'

import time
import threading
import Queue

exitFlag = 0
stopReadFlag = 0
stopWriteFlag = 0
stopEncryptFlag = 0
counterOfQueues = 0
readCount = 0
encryptCount = 0
writeCount = 0
blockNum = 0

threadList = []
threads = []
threadID = 1
readQueue = Queue.Queue()
writeQueue = Queue.Queue()
queueLock = threading.Lock()

alphabet = "abcdefghijklmnopqrstuvwxyz"  

# s, n ve l'i kullanicidan alma
s = int(input("Kaydirma miktarini girin(s): "))
n = int(input("Thread sayisini girin(n): "))
l = int(input("Blok uzunlugunu girin(l): "))

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        process_data(self.name)
        print "Exiting " + self.name
# ---------------------------------------------READING-------------------------------------------------------------
def reading(threadName):
    queueLock.acquire()
    originalFile = open('metin.txt', 'r')
    originalString = originalFile.read()
    j = 0
    while j < len(originalString):
        print threadName + " IS READING: " + original_string[j:j+l]
        readQueue.put(original_string[j:j+l])
        j += l
    originalFile.close()
    queueLock.release()
    return int(len(originalString) / l) + 1
# -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------ENCRYPTING-----------------------------------------------------------
def encrypting(threadName):
    queueLock.acquire()
    currentPart = readQueue.get()
    cryptedData = ''
                                            # sifreleme dongusu
    for character in currentPart:           # metindeki her karakter icin
        if character in alphabet:           # eger karakter alfabede yer aliyorsa
            a = ord(character) - s          # karakterin alfabedeki sirasi + shift
            if a < ord('a'):
                a += 26
            cryptedData += chr(a)
        else:                               # eger karakter alfabede yer almiyorsa
            cryptedData += character
    print threadName + " IS ENCRYPTING:  " + data + "----" + threadName + "---->" + crypted_data
    writeQueue.put(cryptedData)
    queueLock.release()

# -----------------------------------------------------------------------------------------------------------------
# -------------------------------------------------WRITING---------------------------------------------------------
def writing (threadName):
    queueLock.acquire()
    cryptedFile = open('crypted_'+str(s)+'_'+str(n)+'_'+str(l)+'.txt', 'a+')
    while not writeQueue.empty():
        currentPart = writeQueue.get().upper()
        print threadName + " IS WRITING: " + currentPart
        cryptedFile.write(currentPart)
    cryptedFile.close()
    queueLock.release()
# -----------------------------------------------------------------------------------------------------------------

def process_data(threadName):
    global exitFlag
    while not exitFlag:
        global blockNum
        global readCount, encryptCount, writeCount
        global stopReadFlag, stopEncryptFlag, stopWriteFlag

        # ----- METIN'DEN OKUMA KONDISYONU ------
        if blockNum == 0 and stopReadFlag == 0 and threadName == 'Thread-read':
            blockNum = reading(threadName)
            readCount += 1
            if readCount >= blockNum:
                stopReadFlag = 1

        # ----- OKUNANI SIFRELEME KONDISYONU -----
        elif readCount > 0 and stopEncryptFlag == 0 and threadName != 'Thread-read' and threadName != 'Thread-write':
            encrypting(threadName)
            encryptCount += 1
            if encryptCount >= blockNum:
                stopEncryptFlag = 1

        # ----- SIFRELENENI CRYPTED'A YAZMA KONDISYONU -----
        elif encryptCount > 0 and stopWriteFlag == 0 and threadName == 'Thread-write':
            writing(threadName)
            writeCount += 1
            if writeCount >= blockNum:
                stopWriteFlag = 1
                exitFlag = 1
                exit(threads)

        else:
            time.sleep(1)
    
# Create a tread list
threadList.append('Thread-read')
threadList.append('Thread-write')
for i in range(n):
    threadList.append('Thread-' + str(i+1))

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName)              
    thread.start()                                           
    threads.append(thread)                              
    threadID += 1

# tum threadlerin bitmesini bekleme
for t in threads:
    t.join
    
print "Exiting Main Thread - ODEV03"
