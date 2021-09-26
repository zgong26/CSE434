import sys
from socket import *

userDict = {}

print("Port number: ",end="")
port = int(input())
sSocket = socket(AF_INET, SOCK_DGRAM)
sSocket.bind(("", port))
print("Server is now receiving from port", port)

while True:
	oriMessage, cAddress = sSocket.recvfrom(2048)
	message = oriMessage.decode()
	command = message.split(" ")[0]
	if command == "register":
		name = message.split(" ")[1]
		IPv4 = message.split(" ")[2]
		port = message.split(" ")[3]
		if name not in userDict:
			for key in userDict:
				if userDict[key][0] == IPv4 and userDict[key][1] == port:
					sSocket.sendto("FAILURE".encode(), cAddress)
				else:
					userDict[name] = [IPv4, port, "FREE"]
					sSocket.sendto("SUCCESS".encode(), cAddress)
			
		else:
			sSocket.sendto("FAILURE".encode(), cAddress)
		
	if command == "deregister":
		name = message.split(" ")[1]
		if userDict.has_key(name):
			if userDict[name][2] == "FREE":
				del userDict[name]
				sSocket.sendto("SUCCESS".encode(), cAddress)
			else:
				sSocket.sendto("FAILURE".encode(), cAddress)
		else:
			sSocket.sendto("FAILURE".encode(), cAddress)
