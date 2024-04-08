class User:
    # Constructor for user class
    def __init__(self, username, password, balance):
        self.username = username
        self.password = password
        self.balance = balance

    # Deposit - update balance var by transaction amount
    def deposit(self, amount):
        self.balance += amount

    # Withdrawal, - update balance by transaction amount
    def withdraw(self, amount):
        self.balance -= amount
