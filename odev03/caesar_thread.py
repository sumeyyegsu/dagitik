__author__ = 'sumeyye'

import time
import threading
import Queue

exitFlag = 0
threadList = []
threads = []
threadID = 1
readQueue = Queue.Queue()
writeQueue = Queue.Queue()
queueLock = threading.Lock()

alfabe = "abcdefghijklmnopqrstuvwxyz"  
string_lenght = 0
count = 0

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
    original_file = open('metin.txt', 'r')
    original_string = original_file.read()
    j = 0
#    print threadName + " rList.qsize: "+str(readList.qsize()) + "- wList.qsize: "+str(writeList.qsize())
    while j < len(original_string):
        print threadName + " IS READING: " + original_string[j:j+l]
        readQueue.put(original_string[j:j+l])
        j += l
    original_file.close()
    queueLock.release()
    return len(original_string)
# -----------------------------------------------------------------------------------------------------------------
# --------------------------------------------ENCRYPTING-----------------------------------------------------------
def encrypting(threadName):
    queueLock.acquire()
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
    queueLock.release()

# -----------------------------------------------------------------------------------------------------------------
# -------------------------------------------------WRITING---------------------------------------------------------
def writing (threadName):
    queueLock.acquire()
#    crypted_file = open('crypted_'+str(s)+'_'+str(n)+'_'+str(l)+'.txt', 'a+')
    crypted_file = open('crypted.txt', 'w')
    while not writeQueue.empty():
        blok = writeQueue.get().upper()
        print threadName + " IS WRITING: " + blok
        crypted_file.write(blok)
    crypted_file.close()
    queueLock.release()
# -----------------------------------------------------------------------------------------------------------------


def process_data(threadName, q):
    while not exitFlag:
        global string_lenght
        global count
        # okuma listesi bossa ve okuma thread'i geldiyse oku
        if (readQueue.empty()) and (threadName == 'Thread-read'):
            if (readQueue.qsize() != int(string_lenght / l) + 1) and (writeQueue.qsize() != int(string_lenght / l) + 1):
                string_lenght = reading(threadName)
                count = int(string_lenght / l) + 1
        elif (readQueue.qsize() > 0) and (count > 0) and (writeQueue.qsize() != int(string_lenght / l) + 1):
            if (threadName != 'Thread-read') and (threadName != 'Thread-write'):
                encrypting(threadName)
                count -= 1
        elif threadName == 'Thread-write':
            writing(threadName)
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


# Notify threads it's time to exit
exitFlag = 1
    
# tum threadlerin bitmesini bekleme
for t in threads:
    t.join
    
print "Exiting Main Thread"
