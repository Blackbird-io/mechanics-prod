
#structured container for information about company valuation
#

#imports
from .credit_capacity import CreditCapacity
from .enterprise_value import EnterpriseValue
from .val_base import ValBase

#classes
class CompanyValue(ValBase):
    def __init__(self, name = "valuation"):
        ValBase.__init__(self, name)
        self.credit = CreditCapacity()
        self.ev = EnterpriseValue()
        #
        self.tag("valuation", field = "req")


    
        
