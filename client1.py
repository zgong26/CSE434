import sys
import random
from socket import *
import threading
import time
import csv

identifier = -1
ringSize = -1
recMsg = ""
message = ""
leftNei = []
rightNei = []
localDHT = [None] * 353

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
        if(recMsg[0:7] == "SUCCESS"):
            print("SUCCESS")
        if(recMsg[0:7] == "FAILURE"):
            print("FAILURE")

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
            #delay 2 seconds to wait for peers to initialize
            time.sleep(2)
            #leader parses the CSV file
            filename = "StatsCountry.csv"
            rows = []
            fields = []
            with open(filename, encoding="utf8", errors='ignore') as f:
                csvreader = csv.reader(f)
                #disregard the first row
                fields = next(csvreader)
                #store each row into rows array
                for row in csvreader:
                    rows.append(row)
                #here long name is stored as the fourth(3 in index) element in each row
                for row in rows:
                    ascii_sum = 0
                    for ele in row[3]:
                        ascii_sum += ord(ele)
                    pos = ascii_sum % 353
                    peerID = pos % ringSize
                    #change empty str to N/A
                    for x in range(0, 9):
                        if(row[x] == ""):
                            row[x] = "N/A"

                    if(peerID == identifier):
                        localDHT[pos] = row
                        print(row[3] + " is stored")
                                
                    else:
                        #message format for passsing through peers:
                        #construct pos id row[0]...row[8]
                        sendMsg = "construct$"+ str(pos) + "$" + str(peerID)
                        for x in range(0, 9):
                            sendMsg += "$"
                            sendMsg += row[x]
                        cSocket.sendto(sendMsg.encode(), (DHTList[1][1], int(DHTList[1][2])))
                msg = "dht-complete " + DHTList[0][0]
                cSocket.sendto(msg.encode(), (serverIP, serverPort))



        if(recMsg[0:6] == "set-id"):
            msgArr = recMsg.split()
            #remove the first "set-id" term
            msgArr.pop(0)
            identifier = int(msgArr[0])
            msgArr.pop(0)
            ringSize = int(msgArr[0])
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
        
        if(recMsg[0:9] == "construct"):
            msgArr = recMsg.split("$")
            if(int(float(msgArr[2])) == identifier):
                localDHT[int(msgArr[1])] = (msgArr[3], msgArr[4], msgArr[5], msgArr[6], msgArr[7], msgArr[8], msgArr[9], msgArr[10], msgArr[11])
                print(msgArr[6] + " is stored")
            else:
                cSocket.sendto(recMsg.encode(), (rightNei[1], int(rightNei[2])))

            
t1 = threading.Thread(target = keyboard_in)
t2 = threading.Thread(target = recev)

t1.start()
t2.start()

t1.join()
t2.join()
