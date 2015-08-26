#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.market_color
"""

Module defines class of MarketColor objects, which provide a standard record
format for conditions in the credit markets at a given point in time.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
MarketColor           dictionary of industry color, with supplemental attributes
====================  ==========================================================
"""




#imports
import copy

import BBExceptions

from DataStructures.Platform.ID import ID
from Tools import Parsing as parsing_tools

from .corrections import Corrections
from .industry_data import IndustryData
from .inflation import Inflation




#globals
#n/a

#classes
class MarketColor(dict):
    """

    The MarketColor class defines a standard format for recording observed
    market conditions in the fixed income universe on a particular date.

    Class descends from dictionary and stores industry-specific information as
    (k, v) pairs where the value is (usually) a IndustryData record. Class also
    defines some higher level attributes directly on the instance.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    as_of                 date of recorded market conditions
    author                name of instance author
    corrections           instance of Corrections, tracks user adjustments
    id                    instance of Platform.ID.ID class
    inflation             instance of Inflation, tracks expected and observed
    
    FUNCTIONS:
    add_industry()        inserts an IndustryData instance under industry key
    copy()                returns a deep copy of instance
    ====================  ======================================================
    """
    def __init__(self, author, as_of_iso):
        dict.__init__(self)
        self.as_of = parsing_tools.date_from_iso(as_of_iso)
        self.author = author
        #
        self.corrections = Corrections()
        self.id = ID()
        self.inflation = Inflation()
        
    def add_industry(self, industry_name, overwrite = False):
        """


        MarketColor.add_industry(industry_name[, overwrite = False]) -> None


        Method adds industry_name key to instance, with value set to a blank
        IndustryData record. Method will raise CatalogError when instance
        already  contains industry_name, unless ``overwrite`` == True.        
        """
        if industry_name in self:
            if not overwrite:
                c = "Instance already contains a record for ``%s``"
                c = c % industry_name
                raise BBExceptions.CatalogError(c)
        self[industry_name] = IndustryData(industry_name)

    def copy(self):
        """


        MarketColor.copy() -> MarketColor


        Method returns a deep copy of instance. 
        """
        result = copy.deepcopy(self)
        #
        return result

    
