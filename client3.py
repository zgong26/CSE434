import sys
import random
from socket import *

print("Server IP address:")
serverIP = input()

print("Server port number:")
serverPort = int(input())

print("Client port number:")
clientPort = int(input())


cSocket = socket(AF_INET, SOCK_DGRAM)
cSocket.bind(('', clientPort))

while True:
    message = input("Enter the input: ")

    cSocket.sendto(message.encode(), (serverIP, serverPort))
    receivedMessage, serverAddress = cSocket.recvfrom(2048)
    print(receivedMessage.decode())
