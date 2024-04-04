class Transaction:
    def __init__(self, id, payer, amount, payee1, payee1_amnt, payee2 = "None", payee2_amnt = 0, status = 2):
        self.id = id
        self.payer = payer
        self.amount = amount
        self.payee1 = payee1
        self.payee1_amnt = payee1_amnt
        self.status = status
        if(payee2):
            self.payee2 = payee2
            self.payee2_amnt = payee2_amnt

