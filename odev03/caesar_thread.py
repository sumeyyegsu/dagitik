__author__ = 'sumeyye'

import time
from threading import Thread
import Queue

#
j = 0
threads = []            # thread listesi icin degisken tanimiyoruz
workQueue = Queue.Queue()
exitFlag = 0
threadList = []
readList = Queue.Queue()
writeList = Queue.Queue()
cryptedNameList = []
queueLock = threading.Lock()
threadID = 1
alfabe = "abcdefghijklmnopqrstuvwxyz"     # 26 harften olusan alfabeyi tanimlama
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
        
# metni okuma
metin_file = open('metin.txt', 'r')
metin_text = metin_file.read().lower()
metin_file.close()

def threadWork(j, i, s, l):
    print "thread %d" % i
    alphabet = "abcdefghijklmnopqrstuvwxyz"     # 26 harften olusan alfabeyi tanimlama
    crypted_text = ""                           # kripte edilmis metin icin bos bir string tanimiyoruz
                                                # sifreleme dongusu
    if((j+l) <= len(metin_text)):
        print "j: %d" % j
        print "metin_text[j:j+l]: ", metin_text[j:j+l]
        for character in metin_text[j:j+l]:     # metindeki her karakter icin
            if character in alphabet:           # eger karakter alfabede yer aliyorsa
                                                # sagdan sola dairesel kaydirma
                a = ord(character) - s          # karakterin alfabedeki sirasi + shift
                if a < ord('a'):
                    a += 26
                crypted_text += chr(a)
            else:                               # eger karakter alfabede yer almiyorsa
                crypted_text += character
    print "crypted_text: ", crypted_text
    queue.put(crypted_text)
    
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

# crypted metni yazdirma
crypted_file = open('crypted.txt', 'w')
while not queue.empty():
    crypted_file.write(queue.get().upper())
crypted_file.close()
