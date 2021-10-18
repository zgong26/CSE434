import sys
import random
from socket import *

#dictonary for registered clients
userDict = {}
DHTList = []
#if DHT has been setup
DHT_setup = False
#if DHT is under setting up
ifSettingup = False

print("Port number: ", end = "")
port = int(input())
#socket used to bind the port
sSocket = socket(AF_INET, SOCK_DGRAM)
sSocket.bind(('', port))
print("Server is now receiving from port", port)

while True:
    oriMessage, cAddress = sSocket.recvfrom(2048)
    #decode messages
    message = oriMessage.decode()
    command = message.split(" ")[0]

    if command == "register":
        name = message.split(" ")[1]
        IPv4 = message.split(" ")[2]
        port = message.split(" ")[3]
        #check if name exists and if same ip and port exists
        if name not in userDict.keys():
            portNotOverlap = True
            for key in userDict:
                if userDict[key][0] == IPv4 and userDict[key][1] == port:
                    sSocket.sendto("FAILURE".encode(), cAddress)
                    portNotOverlap = False
                    break
            if portNotOverlap:
                userDict[name] = [IPv4, port, "Free"]
                sSocket.sendto("SUCCESS".encode(), cAddress)
        else:
            sSocket.sendto("FAILURE".encode(), cAddress)

    if command == "deregister":
        name = message.split(" ")[1]

    if command == "setup-dht":
        n = message.split(" ")[1]
        n = int(n)
        name = message.split(" ")[2]
        if DHT_setup == True or n < 2 or name not in userDict or n > len(userDict):
            sSocket.sendto("FAILURE".encode(), cAddress)
        else:
            userDict[name][2] = "Leader"
            #append the leader to the first part of DHT
            DHTList.append(tuple([name, userDict[name][0], userDict[name][1]]))
            #randomly choose n-1 free users and set their status to InDHT
            tempDict = userDict.copy()
            del tempDict[name]
            selectedName = random.sample(tempDict.keys(), n-1)
            for w in selectedName:
                userDict[w][2] = "InDHT"
                DHTList.append(tuple([w, userDict[w][0], userDict[w][1]]))
            DHT_setup = True
            result = "SUCCESS_set"
            for t in DHTList:
                result += " " + t[0] + " " + t[1] + " " + t[2]
            sSocket.sendto(result.encode(), (DHTList[0][1], int(DHTList[0][2])))

    if command == "query-dht":
        name = message.split(" ")[1]
        #check if DHT has already been setup, name exists and the status
        if(DHT_setup == False or name not in userDict or userDict[name][2] != "Free"):
            sSocket.sendto("FAILURE".encode(), cAddress)
        else:
            randNum = random.randrange(0, len(DHTList), 1)
            returnMsg = "SUCCESS " + str(DHTList[randNum][0]) + " " + str(DHTList[randNum][1]) + " " + str(DHTList[randNum][2])
            sSocket.sendto(returnMsg.encode(), cAddress)

    if message[0:7] == "query \"":
        msgArr = message.split("\"")
        longName = "querySearch$" + msgArr[1]
        sSocket.sendto(longName.encode(), (DHTList[0][1], int(DHTList[0][2])))


    if command == "leave-dht":
        name = message.split(" ")[1]
        leaderName = message.split(" ")[2]
        sSocket.sendto("DEL".encode(), (userDict[name][0], int(userDict[name][1])))
        if(DHT_setup == False or userDict[name][2] == "Free"):
            sSocket.sendto("FAILURE".encode(), cAddress)
        else:
            #update userDict
            if(leaderName != DHTList[0][0]):
                userDict[leaderName][2] = "Leader"
                userDict[DHTList[0][0]][2] = "InDHT"
                userDict[name][2] = "Free"
                index = 0
                for ele in DHTList:
                    if ele[0] == name:
                        DHTList.remove(ele)
                for ele in DHTList:
                    if ele[0] == leaderName:
                        DHTList.insert(0, DHTList.pop(index))
                    else:
                        index = index + 1
            else:
                userDict[name][2] = "Free"
                for ele in DHTList:
                    if ele[0] == name:
                        DHTList.remove(ele)

            sendMsg = "reset"
            for t in DHTList:
                sendMsg += " " + t[0] + " " + t[1] + " " + t[2]    
            sSocket.sendto(sendMsg.encode(), (DHTList[0][1], int(DHTList[0][2])))

