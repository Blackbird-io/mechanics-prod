#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.statements.balances
"""

Module defines Bundle class, a mix-in for managing objects whose attributes have
similar interfaces.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Bundle                Mix-in class for objects with symmetric attribute values
====================  ==========================================================
"""




# Imports
from .balance_sheet import BalanceSheet

from ..statement_bundle import StatementBundle




# Constants
# n/a

# Globals
# n/a

# Classes
class Balances(StatementBundle):
    """
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    

    FUNCTIONS:
    [load()               connect to prior instance]
    [sever()              copy any existing base and terminate the connection]    
    ====================  ======================================================
    """
    ORDER = ("starting",
             "ending")
    # Use tuple for immutability
     
    def __init__(self, start_date=None, end_date=None):
##        if start_date or end_date:
##            if start_date > end_date:
##                raise Error
        
        self.starting = BalanceSheet(as_of=start_date)
        self.ending = BalanceSheet(as_of=end_date)

##    def load(self, ending_balance):
##        self.starting = ending_balance.copy()


