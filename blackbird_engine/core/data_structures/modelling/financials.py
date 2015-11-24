#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.statement
"""

Module defines Financials, an object that bundles statements. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Financials            a bundle of statements with a minimal shared interface.
====================  ==========================================================
"""




# Imports
import copy

from .statements import Overview, Income




# Constants
# n/a

# Classes
class Financials:
    """
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    ORDER                 tuple; standard processing order
    ordered               list; all statements in ORDER, built dynamically
    
    **statements**
    overview              Statement; general data about an object
    income                Statement; income statement for object
    cash                  Statement; cash flow statement for object
    balance               BalanceSheet; starting and ending balance for object
    ledger                placeholder for object general ledger

    FUNCTIONS:
    build_tables()        built tables for all defined statements
    copy()                return deep copy
    reset()               reset all defined statements
    run_on_all()          perform arbitrary action on all defined statements
    summarize()           summarize all defined statements
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

    def __str__(self):
        """


        Financials.__str__() -> str

        
        Concatenate all defined statements into one string.
        """
        result = ""
        for statement in self.ordered:
            if statement is not None:
                result += str(statement)
            
        return result
    
    @property
    def ordered(self):
        """


        **read-only property**


        Return list of attribute values for all names in instance.ORDERED.
        """
        result = []
        for name in self.ORDER:
            statement = getattr(self, name)
            result.append(statement)
        #
        return result
    
    def build_tables(self, *tagsToOmit):
        """


        Financials.build_tables() -> None


        Build tables for each defined statement.
        """
        self.run_on_all("build_tables", *tagsToOmit)

    def copy(self, enforce_rules=True):
        """


        Financials.copy() -> Financials


        Return deep copy of instance.
        """
        new_instance = copy.copy(self)
        
        for name in self.ORDER:
            own_statement = getattr(self, name, None)
            if own_statement is not None:
                new_statement = own_statement.copy(enforce_rules)
                setattr(new_instance, name, new_statement)
            
        return new_instance
    
    def reset(self):
        """


        Financials.reset() -> None


        Reset each defined statement. 
        """
        self.run_on_all("reset")

    def run_on_all(self, action, *kargs, **pargs):
        """


        Financials.run_on_all() -> None

        
        Run ``statement.action(*kargs, **pargs)`` for all defined statements
        in instance.ordered.

        Expects ``action`` to be a string naming the statement method.
        """
        for statement in self.ordered:
            if statement:
                routine = getattr(statement, action)
                routine(*kargs, **pargs)

    def summarize(self, *tagsToOmit):
        """


        Financials.summarize() -> None


        Summarize each defined statement.
        """
        self.run_on_all("summarize", *tagsToOmit)
            
    #need to inherit tags from statements?   
    
