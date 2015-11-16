#class new fins

from .statements import Overview, Income

class Financials:
    def __init__(self):
        self.overview = Overview()
        self.income = Income()
        self.cash = None
        self.balance = None
        self.ledger = None

    def copy(self):
        pass

    
