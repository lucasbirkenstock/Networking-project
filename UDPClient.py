from socket import *
from user import *
from transaction import *
import sys
import copy
import pickle

def send_and_recieve(req):
    clientSocket.sendto(pickle.dumps(req), (serverName, serverPort))
    res, serverAddress = clientSocket.recvfrom(2048)
    return pickle.loads(res)

def authenticate():
    global curr_user, authenticated, curr_balance, user_transactions
    username = input('Please enter username: ')
    password = input('Please enter password: ')
    req = {"type": "authentication",
               "username": username,
               "password": password}
    res = send_and_recieve(req)

    if res["authenticated"] == "yes":
        curr_user = username
        users.remove(curr_user)
        authenticated = True
        curr_balance = res["balance"]
        user_transactions = res["transactions"]
        print_transactions()
    else:
        print("INVALID CREDENTIALS...\n")
        while 1:
            print("(1) Try again")
            print("(2) Quit")
            choice = input("Enter choice: ")
            if choice == "1":
                authenticate()
                break
            elif choice == "2":
                clientSocket.close()
                sys.exit()
            else:
                print("invalid input! retrying...")

def menu():
    print("(1) Make a transaction.")
    print("(2) Fetch and display the list of transactions.")
    print("(3) Quit the program.")
    choice = input("Please enter choice: ")

    if(choice == "1"):
        pay()
    elif(choice == "2"):
        get_tx()
    elif(choice == "3"):
        clientSocket.close()
        sys.exit()
    else:
        print("invalid input! retrying...")

def pay():
    amount = int(input("How much do you transfer?: "))
    other_users = copy.deepcopy(users)

    print("Who will be Payee 1?")
    print(f"1.{users[0]}")
    print(f"2.{users[1]}")
    print(f"3.{users[2]}")
    choice = input("Enter choice: ")
    payee1 = users[int(choice)-1]
    other_users.remove(payee1)

    payee1_amnt = int(input("How much Payee1 will receive? "))
    while payee1_amnt > amount:
        payee1_amnt = int(input(f"Invalid amount, enter value <= {amount} "))

    payee2 = "None"
    if payee1_amnt < amount:
        print("Who will be Payee 2?")
        print(f"1.{other_users[0]}")
        print(f"2.{other_users[1]}")
        choice = input("Enter choice: ")
        payee2 = other_users[int(choice)-1]

    id = next_id()
    print(f"payee1({payee1}) will recieve {payee1_amnt}BTC, and payee2({payee2}) will recieve {amount-payee1_amnt}")

    tx = Transaction(id, curr_user, amount, payee1, payee1_amnt, payee2, amount-payee1_amnt, status=1)
    user_transactions.append(tx)
    req = {"type": "transaction",
           "transaction": tx}
    res = send_and_recieve(req)

    if(res["status"] == 2):
        print("Payment success!")
        global curr_balance
        curr_balance = res["balance"]
        for tx in user_transactions:
            if tx.id == id:
                tx.status = 2
    if(res["status"] == 3):
        print("Payment Failure! insufficient funds...")
        for tx in user_transactions:
            if tx.id == id:
                tx.status = 3

def next_id():
    id_map = {'A': 99,
              'B': 199,
              'C': 299,
              'D': 399}
    max_id = id_map[curr_user]
    for tx in user_transactions:
        if tx.payer == curr_user and tx.id > max_id:
            max_id = tx.id
    return max_id + 1

def get_tx():
    global curr_balance
    global user_transactions
    req = {"type": "get_tx",
           "username": curr_user}
    res = send_and_recieve(req)

    curr_balance = res["balance"]
    user_transactions = res["tx_list"] + user_transactions
    dedup_tx_list()
    print_transactions()

def dedup_tx_list():
    global user_transactions
    new_list = []
    for tx in user_transactions:
        found = False
        for new_tx in new_list:
            if tx.id == new_tx.id:
                found = True
                break
        if not found:
            new_list.append(tx)
    user_transactions = new_list

def print_transactions():
    print(f"Balance: {curr_balance}")
    print("{:<10} {:<10} {:<10} {:<10} {:<12} {:<14} {:<10} {:<12}".format("Id", "Status", "Payer", "Amount", "Payee1", "Payee1 Amnt", "Payee2", "Payee2 Amnt"))
    print("----------------------------------------------------------------------------------------------")
    for tx in user_transactions:
        print("{:<10} {:<10} {:<10} {:<10} {:<12} {:<14} {:<10} {:<12}".format(tx.id, tx.status, tx.payer, tx.amount, tx.payee1, tx.payee1_amnt, tx.payee2, tx.payee2_amnt))



serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

authenticated = False
curr_balance = 0
user_transactions = []
curr_user = ''
users = ['A', 'B', 'C', 'D']

while not authenticated:
    authenticate()

while 1:
    menu()




