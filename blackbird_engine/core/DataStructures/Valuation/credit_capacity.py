#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.CreditCapacity
"""

Module defines the CreditCapacity class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class CreditCapacity  container for name-specific credit information
====================  ==========================================================

use a path to organize the order
  can have a different path: model.analytics.path
  or can attach the details to the existing path, under the analytics bookmark
    then have one path
    in one place
  problem:
    ic would then include all of the analytics details when forecasting int length?  

the reason why i have all this stuff in analytics is because i was trying to control order before there was a path, because i was really resistant to this idea of a path. 

but now i do have a path. so all of this pre-baked stuff is kind of non-sense. 
  the path provides ordering
  it can contain any object w a guide attribute and tags
    the object doesnt have to be a line item, though it helps if it is (for printing)
  if i need to create bundles of attributes (e.g., "ev") for standard record keeping,
    i can either create lists or classes

make the analytics path separately as default, then call always tack it on to the 
normal one; add "analytics" bookmarks

revised analytics path:
 - compute ev
 - compute abl landscape
 - compute lev landscape


"""




#imports
from .landscape import Landscape
from .val_base import ValBase




#globals
#n/a

#classes
class CreditCapacity(ValBase):
    """

    Class stores Blackbird estimates of company-specific credit outcomes in
    different market segments. Each attribute points to a Landscape object
    that contains data points for transactions in that sector (e.g.,
    ``asset_backed`` loans from banks), organized along key decision axes.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    asset_backed          asset-backed loan price landscape
    bonds                 bond price landscape
    combined              combined loan price landscape
    converts              convertible debt landscape
    lev_loans             leveraged loan price landscape
        
    FUNCTIONS:    
    n/a
    ====================  ======================================================
    
    """

    def __init__(self):
        #
        ValBase.__init__(self)
        self.asset_backed = Landscape()
        self.bonds = None
        self.combined = None
        self.converts = None
        self.lev_loans = Landscape()
        #bonds and converts should be a landscape in the future
                    
                
