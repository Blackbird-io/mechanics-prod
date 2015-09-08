#structured container for information about company valuation
#




#imports
from DataStructures.Modelling.Financials import Financials

from .credit_capacity import CreditCapacity
from .enterprise_value import EnterpriseValue
from .val_base import ValBase




#classes
class CompanyValue(ValBase):
    def __init__(self, name = "valuation"):
        ValBase.__init__(self, name)
        self.credit = CreditCapacity()
        self.ev = EnterpriseValue()
        self.path = None
        #
        self.set_path()
        self.tag("valuation", field = "req")

    def set_path(self):
        path = Financials(populate = False)
        path.autoSummarize = False
        steps = [self.ev,
                 self.credit,
                 self.credit.asset_backed,
                 self.credit.lev_loans]
        path.extend(steps)
        self.path = path


    
        
