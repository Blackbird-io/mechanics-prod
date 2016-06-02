#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.valuation.company_value
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




# Imports
from data_structures.guidance.outline import Outline
from data_structures.modelling.book_mark import BookMark

from .credit_capacity import CreditCapacity
from .enterprise_value import EnterpriseValue




# Constants
# n/a

# Classes
class CompanyValue(Outline):
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
    set_path()            make a list of important attributes for controllers
    ====================  ======================================================
    """
    def __init__(self, name = "valuation"):
        Outline.__init__(self, name)
        self.credit = CreditCapacity()
        self.ev = EnterpriseValue()
        #
        self.set_path()
        self.tags.tag("valuation", field = "req")

    def set_path(self):
        """


        CompanyValue.set_path() -> None


        Method appends a standard valuation roadmap, built out of the instance's own
        attributes, to instance.path.
        """
        Outline.set_path(self)
        steps = [BookMark("start Valuation", "Valuation"),
                 self.ev,
                 self.credit,
                 self.credit.asset_backed,
                 self.credit.lev_loans,
                 BookMark("end Valuation", "Valuation", "endStatement")]
        self.path.extend(steps)


    
        
