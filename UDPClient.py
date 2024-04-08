from socket import *
from user import *
from transaction import *
import sys
import copy
import pickle

# Function to send requests and receive responses from the server
def send_and_recieve(req):
    # Serialize the request and send it to the server
    clientSocket.sendto(pickle.dumps(req), (serverName, serverPort))

    # Store the server's response
    res, serverAddress = clientSocket.recvfrom(2048)

    # Deserialize ther esponse and return it
    return pickle.loads(res)

# Auth function
def authenticate():
    # Vars
    global curr_user, authenticated, curr_balance, user_transactions

    # Take in user input for username and password
    username = input('Please enter username: ')
    password = input('Please enter password: ')

    # Formulate request to send to the server, including username and password
    req = {"type": "authentication",
               "username": username,
               "password": password}
    
    # Send request to the send and receive function, which returns the server's response. 
    res = send_and_recieve(req)

    # If the response indicates a successful authentication:
    if res["authenticated"] == "yes":
        
        # Updates variables and prints transactions
        curr_user = username
        users.remove(curr_user)
        authenticated = True
        curr_balance = res["balance"]
        user_transactions = res["transactions"]
        print_transactions()

    # If authentication fails:
    else:
        # Print error message
        print("INVALID CREDENTIALS...\n")

        # In an infinite loop, prompt for new input to login
        while 1:
            # Prompt input
            print("(1) Try again")
            print("(2) Quit")
            choice = input("Enter choice: ")

            # If user wants to try again:
            if choice == "1":
                # Call this function again, then break
                authenticate()
                break
            # Exit program if user doesn't want to try again
            elif choice == "2":
                clientSocket.close()
                sys.exit()
            # Invalid input: loop through again
            else:
                print("invalid input! retrying...")

# Function for printing menu and prompting user input
def menu():
    # Print the menu
    print("(1) Make a transaction.")
    print("(2) Fetch and display the list of transactions.")
    print("(3) Quit the program.")

    # Prompt user input
    choice = input("Please enter choice: ")

    # Call functions or print an error based on input
    if(choice == "1"):
        pay()
    elif(choice == "2"):
        get_tx()
    elif(choice == "3"):
        clientSocket.close()
        sys.exit()
    else:
        print("invalid input! retrying...")

# Pay function
def pay():
    # Prompt authenticated user for how much they want to send
    amount = int(input("How much do you transfer?: "))
    other_users = copy.deepcopy(users)

    # Prompt for recipient #1 (mandatory)
    print("Who will be Payee 1?")
    print(f"1.{users[0]}")
    print(f"2.{users[1]}")
    print(f"3.{users[2]}")
    choice = input("Enter choice: ")

    # Set payee var to user input, remove that user from list of available payees for a second payee to reflect that
    payee1 = users[int(choice)-1]
    other_users.remove(payee1)

    # Prompt for amount to send to payee 1
    payee1_amnt = int(input("How much Payee1 will receive? "))

    # While the user attempts to send more to payee 1 than the overall amount they want to send:
    while payee1_amnt > amount:
        # Reprompt the user
        payee1_amnt = int(input(f"Invalid amount, enter value <= {amount} "))

    payee2 = "None"

    # If the user doesn't want to send the entire balance to payee 1:
    if payee1_amnt < amount:

        # Prompt for second recipient
        print("Who will be Payee 2?")
        print(f"1.{other_users[0]}")
        print(f"2.{other_users[1]}")
        choice = input("Enter choice: ")
        payee2 = other_users[int(choice)-1]

    # Generate next transaction id, store it
    id = next_id()

    # Print tx info
    print(f"payee1({payee1}) will recieve {payee1_amnt}BTC, and payee2({payee2}) will recieve {amount-payee1_amnt}")

    # Create transaction object
    tx = Transaction(id, curr_user, amount, payee1, payee1_amnt, payee2, amount-payee1_amnt, status=1)

    # Append the created transaction to the transaction list
    user_transactions.append(tx)

    # Formulate request to the server
    req = {"type": "transaction",
           "transaction": tx}
    
    # Send request to the server and store its response
    res = send_and_recieve(req)

    # If the response has status 2:
    if(res["status"] == 2):
        # Print a success msg, update current balance var
        print("Payment success!")
        global curr_balance
        curr_balance = res["balance"]

        # For every transaction in the user's transaction list,
        for tx in user_transactions:
            # If the transaction id matches the id of this particular transaction, set its status to 2 [1 is default]
            if tx.id == id:
                tx.status = 2
    
    # If the response has status 3:
    if(res["status"] == 3):
        # Print failure message
        print("Payment Failure! insufficient funds...")

        # If the transaction id matches the id of this particular transaction, set its status to 3 [1 is default]
        for tx in user_transactions:
            if tx.id == id:
                tx.status = 3

# Function for generating the next ID
def next_id():
    # Map users to certain numbers
    id_map = {'A': 99,
              'B': 199,
              'C': 299,
              'D': 399}
    
    # Set the max id based on map
    max_id = id_map[curr_user]

    # For each transaction in a user's transaction list:
    for tx in user_transactions:
        # Update max Id if necessary
        if tx.payer == curr_user and tx.id > max_id:
            max_id = tx.id
    # Return max + 1
    return max_id + 1


# Get transaction list
def get_tx():
    global curr_balance
    global user_transactions

    # Formulate request to send to server
    req = {"type": "get_tx",
           "username": curr_user}
    
    # Send request to erver, store response 
    res = send_and_recieve(req)

    # Extract current balance and user transaction list from the server response
    curr_balance = res["balance"]
    user_transactions = res["tx_list"] + user_transactions

    # Call helper functions
    dedup_tx_list()
    print_transactions()


# Delete duplicate transactions in transaction list
def dedup_tx_list():
    global user_transactions
    new_list = []

    # Interate through each transaction in a user's transaction list
    for tx in user_transactions:
        found = False

        # If there is a match/duplicate , break and do not append the transaction
        for new_tx in new_list:
            if tx.id == new_tx.id:
                found = True
                break

        # If not a duplicate, append the transaction to the new list
        if not found:
            new_list.append(tx)
    
    # Set transaction list to the newly created list without dupes
    user_transactions = new_list

# Print each transaction in a user's transaction list
def print_transactions():
    print(f"Balance: {curr_balance}")
    print("{:<10} {:<10} {:<10} {:<10} {:<12} {:<14} {:<10} {:<12}".format("Id", "Status", "Payer", "Amount", "Payee1", "Payee1 Amnt", "Payee2", "Payee2 Amnt"))
    print("----------------------------------------------------------------------------------------------")
    for tx in user_transactions:
        print("{:<10} {:<10} {:<10} {:<10} {:<12} {:<14} {:<10} {:<12}".format(tx.id, tx.status, tx.payer, tx.amount, tx.payee1, tx.payee1_amnt, tx.payee2, tx.payee2_amnt))


# Set up UDP connection to port 12000
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Var setup/init
authenticated = False
curr_balance = 0
user_transactions = []
curr_user = ''
users = ['A', 'B', 'C', 'D']

while not authenticated:
    authenticate()

while 1:
    menu()




