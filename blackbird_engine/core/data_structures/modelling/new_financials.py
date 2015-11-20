#class new fins

import copy

from .statements import Overview, Income

class Financials:
    """
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    ORDER                 standard processing order
    
    **statements**
    overview
    income
    cash
    balance
    ledger

    FUNCTIONS:
    copy()                return deep copy
    ====================  ======================================================
    """
    ORDER = ("overview",
             "income",
             "cash",
             "balance",
             "ledger")
    # tuple for immutability
    
    def __init__(self):
        self.overview = Overview()
        self.income = Income()
        self.cash = None
        self.balance = None
        self.ledger = None

    @property
    def ordered(self):
        result = []
        for name in self.ORDER:
            statement = getattr(self, name)
            result.append(statement)
        #
        return result

    def copy(self, enforce_rules=True):
        """


        Financials.copy() -> Financials


        Return deep copy.
        """
        new_instance = copy.copy(self)
        
        for name in self.ORDER:
            own_statement = getattr(self, name)
            if own_statement:
                new_statement = own_statement.copy(enforce_rules)
                setattr(new_instance, name, new_statement)
            
        return new_instance
    

    def build_tables(self, *tagsToOmit):
        for statement in self.ordered:
            if statement:
                statement.build_tables(*tagsToOmit)

    def reset(self):
        for statement in self.ordered:
            if statement:
                statement.reset()

    def summarize(self, *tagsToOmit):
        for statement in self.ordered:
            if statement:
                statement.summarize(*tagsToOmit)

    ### can probably just delegate unspecified methods generically
            
    def __str__(self):
        """
        Return concatenated string of all other statements
        """
        result = ""
        for statement in self.ordered:
            result += str(statement)
            
        return result
            
    #need to inherit tags from statements?
    #
    
    
