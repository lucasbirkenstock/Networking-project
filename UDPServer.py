from socket import *
from user import *
from transaction import *
import pickle

def transactions_by_user(username):
    new_list = []
    for tx in transactions:
        if tx.payer == username or tx.payee1 == username or tx.payee2 == username:
            new_list.append(tx)
    return new_list

users = {'A': User('A', 'A', 10),
         'B': User('B', 'B', 10),
         'C': User('C', 'C', 10),
         'D': User('D', 'D', 10),}



transactions = []

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print ('The server is ready to receive')
while 1:
    req, clientAddress = serverSocket.recvfrom(2048)
    req = pickle.loads(req)

    if req["type"] == "authentication":
        username = req["username"]
        password = req["password"]
        if(users[username].password == password):
            res = {"authenticated": "yes",
                   "balance": users[username].balance,
                   "transactions": transactions_by_user(username)}
        else:
            res = {"authenticated": "no"}
        serverSocket.sendto(pickle.dumps(res), clientAddress)

    elif req["type"] == "transaction":
        tx = req["transaction"]
        if users[tx.payer].balance >= tx.amount:
            tx.status = 2
            transactions.append(tx)
            users[tx.payer].withdraw(tx.amount)
            users[tx.payee1].deposit(tx.payee1_amnt)
            if(tx.payee2 != "None"):
                users[tx.payee2].deposit(tx.payee2_amnt)
            res = {"status": 2,
                   "balance": users[tx.payer].balance}
        else:
            res = {"status": 3}
        serverSocket.sendto(pickle.dumps(res), clientAddress)

    elif req["type"] == "get_tx":
        username = req["username"]
        tx_list = transactions_by_user(username)
        balance = users[username].balance
        res = {"balance": balance,
               "tx_list": tx_list}
        serverSocket.sendto(pickle.dumps(res), clientAddress)
    else:
        print("i dont know")
