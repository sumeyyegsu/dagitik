__author__ = 'sumeyye'

import time
from threading import Thread
import Queue

exitFlag = 0
threadList = []
threads = []
threadID = 1
readQueue = Queue.Queue()
writeQueue = Queue.Queue()
queueLock = threading.Lock()
workQueue = Queue.Queue()

alfabe = "abcdefghijklmnopqrstuvwxyz"  
string_lenght = 0
count = 0

# s, n ve l'i kullanicidan alma
s = int(input("Kaydirma miktarini girin: "))
n = int(input("Thread sayisini girin: "))
l = int(input("Blok uzunlugunu girin: "))

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name
        
# ---------------------------------------------READING-------------------------------------------------------------
def reading(threadName):
    original_file = open('metin.txt', 'r')
    original_string = original_file.read()
    j = 0
#    print threadName + " rList.qsize: "+str(readList.qsize()) + "- wList.qsize: "+str(writeList.qsize())
    while j < len(original_string):
        print threadName + " IS READING: " + original_string[j:j+l]
        readQueue.put(original_string[j:j+l])
        j += l
    original_file.close()
    return len(original_string)
# -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------ENCRYPTING-----------------------------------------------------------
def encrypting(threadName):
    data = readQueue.get()
    crypted_data = ""
                                            # sifreleme dongusu
    for character in data:                  # metindeki her karakter icin
        if character in alfabe:             # eger karakter alfabede yer aliyorsa
            a = ord(character) - s          # karakterin alfabedeki sirasi + shift
            if a < ord('a'):
                a += 26
            crypted_data += chr(a)
        else:                               # eger karakter alfabede yer almiyorsa
            crypted_data += character
#    print threadName + " rList.qsize: "+str(readList.qsize()) + "- wList.qsize: "+str(writeList.qsize())
    print threadName + " IS ENCRYPTING:  " + data + "----" + threadName + "---->" + crypted_data
    writeQueue.put(crypted_data)

# -----------------------------------------------------------------------------------------------------------------
# -------------------------------------------------WRITING---------------------------------------------------------
def writing (threadName):
    crypted_file = open('crypted.txt', 'w')
    while not writeQueue.empty():
        s = writeQueue.get().upper()
        print threadName + " IS WRITING: " + s
        crypted_file.write(s)
    crypted_file.close()
# -----------------------------------------------------------------------------------------------------------------


def process_data(threadName, q):
    while not exitFlag:
        global string_lenght
        global count
        queueLock.acquire()
        # okuma listesi bossa ve okuma thread'i geldiyse oku
        if (readQueue.empty()) and (threadName == 'Thread-read'):
            if (readQueue.qsize() != int(string_lenght / l) + 1) and (writeQueue.qsize() != int(string_lenght / l) + 1):
                string_lenght = reading(threadName)
                count = int(string_lenght / l) + 1
            queueLock.release()                             # kilidi ac
        else:
#            print "readList.qsize: " + str(readList.qsize())
            if (readQueue.qsize() > 0) and (count > 0) and (writeQueue.qsize() != int(string_lenght / l) + 1):
                if (threadName != 'Thread-read') and (threadName != 'Thread-write'):
                    encrypting(threadName)
                    count -= 1
                queueLock.release()
            elif (threadName == 'Thread-write'):
                writing(threadName)
                queueLock.release()
            else:
                queueLock.release()                     # kilidi ac
                time.sleep(0.5)


    
# Create a tread list
for i in range(n):
    threadList.append('Thread-' + str(i+1))
threadList.append('Thread-read')
threadList.append('Thread-write')

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName,, workQueue)      # yeni bir thread yaratma
    thread.start()                                           # thread'i baslatma/run etme
    threads.append(thread)                                   # thread'i threads listesine ekleme
    threadID += 1

    
# Fill the queue        # write ve read threadleri rezerve oldugunda buraya atmiyoruz!!!
queueLock.acquire()
for i in range(n):
    workQueue.put(i+1)
queueLock.release()


# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1
    
# tum threadlerin bitmesini bekleme
for t in threads:
    t.join
    
print "Exiting Main Thread"
