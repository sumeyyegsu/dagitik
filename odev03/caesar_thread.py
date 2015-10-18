__author__ = 'sumeyye'

import time
from threading import Thread

#
j = 0

# s, n ve l'i kullanicidan alma
s = int(input("Kaydirma miktarini girin: "))
n = int(input("Thread sayisini girin: "))
l = int(input("Blok uzunlugunu girin: "))

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


#istenen sayida(n) thread'i yaratip gerekli islemleri yaptigimiz dongu
for i in range(n):
    t = Thread(target=threadWork, args=(j, i, s, l))    # yeni bir thread yaratma
    t.start()                                           # thread'i baslatma/run etme
    threads.append(t)                                   # thread'i threads listesine ekleme
    j += l
    
# tum threadlerin bitmesini bekleme
for t in threads:
    t.join

# crypted metni yazdirma
crypted_file = open('crypted.txt', 'w')
crypted_file.write(crypted_text.upper())
crypted_file.close()
