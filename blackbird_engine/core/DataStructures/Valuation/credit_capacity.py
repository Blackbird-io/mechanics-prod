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
    ic would then include?  

the reason why i have all this stuff in analytics is because i was trying to control order before there was a path, because i was really resistant to this idea of a path. 

but now i do have a path. so all of this pre-baked stuff is kind of non-sense. 
  the path provides ordering
  it can contain any object w a guide attribute and tags
    the object doesnt have to be a line item, though it helps if it is (for printing)
  if i need to create bundles of attributes (e.g., "ev") for standard record keeping,
    i can either create lists or classes

change "parameters" to "schema"

make the analytics path separately as default, then call always tack it on to the 
normal one; add "analytics" bookmarks

revised analytics path:
 - compute ev
 - compute abl landscape
 - compute lev landscape


"""




#imports
from .price_landscape import Landscape




#globals
#n/a

#classes
class CreditCapacity:
    """

    Class covers Blackbird estimates of credit market outcomes. Instances
    provide an interface for storing and organizing various facets of that
    information.

    The ``landscape`` attribute provides a snapshot of credit references keyed by
    price and size. Each of those keys points towards a dictionary keyed by
    their respective values (ie percent cost or size in millions). The price and
    size dictionaries then contain values for their counterpart in dictionary
    format, keyed "bad", "medium", "good". 
   
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    abl                   asset-backed loan price landscape for company
    cf                    leveraged loan price landscape for company
    bonds                 bond price landscape
    combined              combined loan price landscape for company                  
        
    FUNCTIONS:    
    combine()             pick lowest price generally? or populate a scenario w all the keys
                          #pick lowest price, can also average the prices where necessary
    ====================  ======================================================
    
    """

    def __init__(self):
        #
        self.asset_backed = Landscape()
        self.bonds = None
        self.combined = None
        self.converts = None
        self.lev_loans = Landscape()
        #bonds and converts should be a landscape in the future
        
    def combine(self):
        """

        blend data from all known landscapes

        rules:
        - always pick the lowest price
        """
        #routine here:
        #make a new landscape.
        #run landscape.combine(*feeder_fields)
        #run landscape.label()
        #thats it
        
        #routine:
        #(1) sort the surfaces by price
        #(2) start w the cheapest surface
        #(3) copy all the datapoints in that surface to the combined
        #(4) also add datapoints from other surfaces that are within range on the scoring var
            #
            #(a) for every datapoint in that surface, get a forecast from every other surface
            #(b) if the forecast is within range of base on the scoring var, record it under the scoring var.
            #(c) otherwise, discard it.
        #(6) repeat with all others, but not for values within the range we have already done
        #(7) update labels
                    
                
