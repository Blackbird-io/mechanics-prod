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

    def refresh(self):
        for statement in self.path:
            statement.build_index()

    def view(self):
        """
        
        """

    def __str__(self):
        """
        Return concatenated string of all other statements
        """
        pass

    #need to inherit tags?
    
    
