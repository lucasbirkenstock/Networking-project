from socket import *

serverPort = 12000 # set same port as client

serverSocket = socket(AF_INET, SOCK_DGRAM) # create a UDP socket

serverSocket.bind(('', serverPort)) # bind the socket to the port 12000