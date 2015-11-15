
__author__ = 'sumeyye'

import sys
import socket
import threading
import time
import Queue
from PyQt4.QtGui import *

''' ------------------------------------------- MYREADTHREAD ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# soket uzerinden veri bekleyecek, veri geldiginde incoming_parser()'i calistiracak
# cevap verilecekse eger, istemciye cevap dondurecek
class myReadThread (threading.Thread):
    def __init__(self, clientSocket, app):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.app = app

    # socket uzerinden gelen mesajlari degerlendirip buna gore hareketler tanimlayacak
    def incoming_parser(self, data):

        if len(data) == 0:
            return
        if len(data) > 3 and data[3] == " ":

            rest = data[4:]
            if data[0:3] == "HEL":
                response = "SERVER: Registered as " + rest + "."
                print response
            elif data[0:3] == "REJ":
                response = "SERVER: Rejected " + rest + "."
                print response
                self.cSocket.close()
            elif data[0:3] == "BYE":
                response = "SERVER: Bye " + rest
                print response
                self.cSocket.close()
            elif data[0:3] == "ERL":
                response = "SERVER: Register first."
                print response
            elif data[0:3] == "MNO":
                response = "SERVER: User " + rest + " does not exist."
                print response
            elif data[0:3] == "SYS":
                response = "SERVER:" + rest
                print response
            elif data[0:3] == "LSA":
			    response = "SERVER: Registered users " + rest + "."
			    print response
            elif data[0:3] == "SOK" or data[0:3] == "MOK":
                response = "SERVER: Message sent successfully."
                print response
            else:
                response = data
        else:
            response = "SERVER: Command error."
        return response


    def run(self):
         while True:
            data = self.clientSocket.recv(buff)
            response = self.incoming_parser(data)
            self.threadQueue.put(response + "(" + time.strftime("%H:%M:%S") + ")")

''' ------------------------------------------- MYWRITETHREAD ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# threadQueue'da mesaj varsa bunlari soket uzerinden gonderecek
class WriteThread_Client (threading.Thread) :
    def __init__(self, clientSocket,threadQueue):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.threadQueue = threadQueue

    def run(self):
            while True :
                if self.threadQueue.qsize() > 0:
                    queueMessage = self.threadQueue.get()
                    try:
                    	print "Server'a gonderilen mesaj: " + queueMessage
                        self.clientSocket.send(queueMessage)
                    except socket.error:
                        self.clientSocket.close()
                        break

''' ------------------------------------------- CLIENTDIALOG ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Qt tabanli grafik arabirim
class ClientDialog(QDialog) :
    def __init__(self, threadQueue):
        self.qt_app = QApplication(sys.argv)
        QDialog.__init__(self,None)
        self.threadQueue = threadQueue
        self.setWindowTitle('IRC Client (Sumeyye KONAK)')
        self.setMinimumSize(500,200)
        self.vbox = QVBoxLayout()
        self.sender = QLineEdit("", self)
        self.channel = QTextBrowser()
        self.send_button = QPushButton('&Send')
        self.send_button.clicked.connect(self.outgoing_parser)
        self.vbox.addWidget(self.channel)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.setLayout(self.vbox)

    def cprint (self, data):
        self.channel.append(data)

    def outgoing_parser(self):
        data = self.sender.text()
        if len(data) == 0:
            return

        elif data[0] == "/":

            if data[1:5] == "nick":
                self.threadQueue.put("USR " + data[5:])
            if data[1:5] == "list":
                self.threadQueue.put("LSQ")
            elif data[1:5] == "quit":
                self.threadQueue.put("QUI")
            elif data[1:5] == "msg":
                msg = str.split(data[5:], " ", 1)
                nickname = msg[0]
                message = msg[1]
                self.threadQueue.put("MSG " + nickname + " " + message)
            else:
                self.cprint("LOCAL: Command error.")
        else:
            self.threadQueue.put("SAY " + data)
        self.sender.clear()

    def run(self):
        '''Run the app and show the main from.'''
        self.show()
        self.qt_app.exec_()



buff = 2048

s = socket.socket()
host = socket.gethostname()
port = 12345
s.connect((host, port))
print ("Baglanti kuruldu")

threadQueue = Queue.Queue()
app = ClientDialog(threadQueue)

readThread = myReadThread(s, app)
readThread.start()

writeThread = WriteThread_Client(s, threadQueue)
writeThread.start()

app.run()

readThread.join()
writeThread.join()
s.close()
