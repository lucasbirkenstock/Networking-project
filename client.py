from socket import *

serverName = 'hostname' # equivalent of localhost
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM) # create UDP socket for the server

