from socket import *

serverPort = 12000 # set same port as client
serverSocket = socket(AF_INET, SOCK_DGRAM) # create a UDP socket
serverSocket.bind(('', serverPort)) # bind the socket to the port 12000

# For each user, the server stores username, password, and current balance.
class user: 
    username = ''
    password = '' 
    btc_balance = 10.0

# The server also stores a list of confirmed TXs. Each TX has 1 payer and 1-2 payee(s) and the
# amount that the payer has paid, and each payee has received. Initially this list is empty.

class confirmed_tx:

     def __init__(self, payer_input, payee_list_input):  # Constructor
        self.payee_list = payee_list_input  # Initialize payee_list as a member variable
        self.payer = payer_input  # Initialize payer as a member variable



