from socket import *
from user import *
from transaction import *
import pickle

# List all transactions made by a particular user
def transactions_by_user(username):
    # Create empty list for storing transactions attributed to a user
    new_list = []

    # For every transaction in the overall transaction list: 
    for tx in transactions:
        # If the particular user's username is in it, add this transaction to the new list
        if tx.payer == username or tx.payee1 == username or tx.payee2 == username:
            new_list.append(tx)

    # Return the new list
    return new_list

# Map usernames to user objects
users = {'A': User('A', 'A', 10),
         'B': User('B', 'B', 10),
         'C': User('C', 'C', 10),
         'D': User('D', 'D', 10),}

# Create empty list for storing transactions
transactions = []

# UDP connection setup
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Configure server to listen for any connection on the specified port
serverSocket.bind(('', serverPort))
print ('The server is ready to receive')

# Infinitely loop:
while 1:
    # Receive req, clientaddress from the client
    req, clientAddress = serverSocket.recvfrom(2048)
    # Deserialize req to reconstruct the original object
    req = pickle.loads(req)

    # If the request from the client is an authentication request:
    if req["type"] == "authentication":
        # Extract username and password from the request
        username = req["username"]
        password = req["password"]

        # If password matches:
        if(users[username].password == password):
            # Set the response to the request. Include login success status, balance, and a list of transactions for the user. 
            res = {"authenticated": "yes",
                   "balance": users[username].balance,
                   "transactions": transactions_by_user(username)}
        # If login fails, set response to denote authentication as failed. 
        else:
            res = {"authenticated": "no"}

        # Serialize the server response and send it to the client
        serverSocket.sendto(pickle.dumps(res), clientAddress)

    # If the request is a transaction type:
    elif req["type"] == "transaction":

        # Store tx from the client transaction
        tx = req["transaction"]

        # If a user has the available balance to perform the transaction:
        if users[tx.payer].balance >= tx.amount:

            # Update tx status, add the transaction to the list, and update wallet balances for the payee and payer.
            tx.status = 2
            transactions.append(tx)
            users[tx.payer].withdraw(tx.amount)
            users[tx.payee1].deposit(tx.payee1_amnt)

            # If there's a second payee for this transaction: 
            if(tx.payee2 != "None"):
                # Deposit to this second payee also. 
                users[tx.payee2].deposit(tx.payee2_amnt)
            
            # Formulate the response, including the transaction's status and payer's balance. 
            res = {"status": 2,
                   "balance": users[tx.payer].balance}
            
        # If the payer doesn't have the balance to perform the attempted transaction:
        else:
            # Formulate response to only include the status 
            res = {"status": 3}

        # Serialize the response and send to the client
        serverSocket.sendto(pickle.dumps(res), clientAddress)

    # If the request is a get_tx type:
    elif req["type"] == "get_tx":

        # Extract the username, transactinon list for that user, and that user's balance
        username = req["username"]
        tx_list = transactions_by_user(username)
        balance = users[username].balance

        # Formulate response to client
        res = {"balance": balance,
               "tx_list": tx_list}
        
        # Serialize the response and send it to the client
        serverSocket.sendto(pickle.dumps(res), clientAddress)
    else:
        print("i dont know")
