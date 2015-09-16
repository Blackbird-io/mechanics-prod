#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Markets.company_value
"""

Module defines a standard storage format for information about the market value
of a company.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
CompanyValue          standard form for storing data about company value
====================  ==========================================================
"""




#imports
from DataStructures.Modelling.BookMark import BookMark
from DataStructures.Modelling.Financials import Financials
from DataStructures.Guidance.stage import Stage

from .credit_capacity import CreditCapacity
from .enterprise_value import EnterpriseValue




#globals
#n/a

#classes
class CompanyValue(Stage):
    """

    This class manages protocols that provide a focal point for MatchMaker
    analysis. Daughter of Controller class.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    credit                information about company-specific credit outcomes
    ev                    information about company enterprise value
    path                  ordered container of attributes to consider
    
    FUNCTIONS:
    build_path()          make a list of important attributes for controllers
    ====================  ======================================================
    """
    def __init__(self, name = "valuation"):
        Stage.__init__(self, name)
        self.credit = CreditCapacity()
        self.ev = EnterpriseValue()
        #
        self.build_path()
        self.tag("valuation", field = "req")

    def build_path(self):
        """


        CompanyValue.set_path() -> None


        Method appends a standard valuation roadmap, built out of the instance's own
        attributes, to instance.path.
        """
        steps = [BookMark("start Valuation", "Valuation"),
                 self.ev,
                 self.credit,
                 self.credit.asset_backed,
                 self.credit.lev_loans,
                 BookMark("end Valuation", "Valuation", "endStatement")]
        self.path.extend(steps)


    
        
