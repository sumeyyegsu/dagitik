
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
        rest = data[4:]
        if data[0:3] == "HEL":
            response = "Registered as <" + rest + ">."
        elif data[0:3] == "REJ":
            response = "Rejected <" + rest + ">."
            self.clientSocket.close()
        elif data[0:3] == "BYE":
            response = "Bye " + rest
            self.clientSocket.close()
        elif data[0:3] == "ERL":
            response = "Register first."
        elif data[0:3] == "ERR":
            response = "Command error."
        elif data[0:3] == "MNO":
            response = "User " + rest + " does not exist."
        elif data[0:3] == "SYS":
            response = rest
        elif data[0:3] == "LSA":
            if data.find(':') != -1:
			    response = "Registered users " + rest + "."
            else:
                response = "There is no nickname registered."
        elif data[0:3] == "SOK" or data[0:3] == "MOK":
            response = "Message sent successfully."
        else:
            response = data
        self.app.cprint(response + "(" + time.strftime("%H:%M:%S") + ")")
        
    def run(self):
         while True:
            data = str(self.clientSocket.recv(buff))
            self.incoming_parser(data)

''' ------------------------------------------- MYWRITETHREAD ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# threadQueue'da mesaj varsa bunlari soket uzerinden gonderecek
class WriteThread_Client (threading.Thread) :
    def __init__(self, clientSocket, threadQueue):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.threadQueue = threadQueue

    def run(self):
            while True :
                queueMessage = str(self.threadQueue.get())
                try:
                    self.clientSocket.send(queueMessage)
                except socket.error:
                    self.clientSocket.close()
                    break

''' ------------------------------------------- CLIENTDIALOG ---------------------------------------------------- '''
''' ------------------------------------------------------------------------------------------------------------- '''
# Qt tabanli grafik arabirim
class ClientDialog(QDialog) :
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        QDialog.__init__(self,None)
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
        self.cprint("Local: " + data + "(" + time.strftime("%H:%M:%S") + ")")
        if len(data) == 0:
            return

        elif data[0] == "/":

            if data[1:5] == "nick":
                threadQueue.put("USR " + data[6:])
            if data[1:5] == "list":
                threadQueue.put("LSQ")
            elif data[1:5] == "quit":
                threadQueue.put("QUI")
            elif data[1:5] == "msg ":
                msg = data.split(" ")
                nickname = msg[0]
                message = msg[1]
                threadQueue.put("MSG " + nickname + ":" + message)
            else:
                threadQueue.put("Command error. Try again.")
        else:
            threadQueue.put("SAY " + data)
        self.sender.clear()

    def run(self):
        self.show()
        self.qt_app.exec_()

buff = 2048

s = socket.socket()
host = socket.gethostname()
port = 12345
s.connect((host, port))

threadQueue = Queue.Queue()

app = ClientDialog()

readThread = myReadThread(s, app)
readThread.daemon = True
readThread.start()

writeThread = WriteThread_Client(s, threadQueue)
writeThread.daemon = True
writeThread.start()

app.run()

readThread.join()
writeThread.join()
s.close()
