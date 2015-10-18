__author__ = 'sumeyye'

import time
from threading import Thread

#
j = 0
fin = None

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


for i in range(n):
    t = Thread(target=threadWork, args=(j,i,))
    t.start()
    j += l
    if(j > len(metin_text)):
        fin = True

if fin == True:
    # crypted metni yazdirma
    crypted_file = open('crypted.txt', 'w')
    crypted_file.write(crypted_text.upper())
    crypted_file.close()
