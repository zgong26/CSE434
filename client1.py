import sys
import random
from socket import *
import threading

identifier = -1
ringSize = -1
recMsg = ""
message = ""
leftNei = []
rightNei = []

print("Server IP address:")
serverIP = input()

print("Server port number:")
serverPort = int(input())

print("Client port number:")
clientPort = int(input())


cSocket = socket(AF_INET, SOCK_DGRAM)
cSocket.bind(('', clientPort))

def keyboard_in():
    while True:
        global message
        message = input()
        cSocket.sendto(message.encode(), (serverIP, serverPort))
        #receivedMessage, serverAddress = cSocket.recvfrom(2048)
        #recMsg = receivedMessage.decode()
        #print(recMsg)

def recev():
    while True:
        global identifier
        global ringSize
        receivedMessage, serverAddress = cSocket.recvfrom(2048)
        recMsg = receivedMessage.decode()
        print(recMsg)

        #leader situation:
        if(message[0:5] == "setup" and receivedMessage.decode()[0:7] == "SUCCESS"):
            msgArr = recMsg.split()
            #remove the first "SUCCESS" term
            msgArr.pop(0)
            ringSize = len(msgArr) / 3
            identifier = 0
            #reform DHTList
            DHTList = []
            for x in range(0, int(ringSize*3), 3):
                DHTList.append(tuple([msgArr[x], msgArr[x+1], msgArr[x+2]]))
            for t in range(1, int(ringSize)):
                sendMsg = "set-id " + str(t) + " " + str(int(ringSize)) + " " + DHTList[(t-1)%int(ringSize)][0] + " "+ DHTList[(t-1)%int(ringSize)][1] + " " + DHTList[(t-1)%int(ringSize)][2] + " " + DHTList[(t+1)%int(ringSize)][0] + " " + DHTList[(t+1)%int(ringSize)][1] + " " + DHTList[(t+1)%int(ringSize)][2]
                cSocket.sendto(sendMsg.encode(), (DHTList[t][1], int(DHTList[t][2])))

        if(recMsg[0:6] == "set-id"):
            msgArr = recMsg.split()
            #remove the first "set-id" term
            msgArr.pop(0)
            identifier = msgArr[0]
            msgArr.pop(0)
            ringSize = msgArr[0]
            msgArr.pop(0)
            global leftNei
            global rightNei
            #store left/right neighbors' information
            leftNei.append(msgArr[0])
            leftNei.append(msgArr[1])
            leftNei.append(msgArr[2])
            rightNei.append(msgArr[3])
            rightNei.append(msgArr[4])
            rightNei.append(msgArr[5])
            

            
t1 = threading.Thread(target = keyboard_in)
t2 = threading.Thread(target = recev)

t1.start()
t2.start()

t1.join()
t2.join()
