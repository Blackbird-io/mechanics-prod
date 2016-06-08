# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.valuation.credit_capacity
"""

Module defines a standard storage format for name-specific views of the fixed
income universe.
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
"""




#imports
import copy

from .landscape import Landscape

from ..guidance.step import Step




#globals
#n/a

#classes
class CreditCapacity(Step):
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
    combined              landscape across all market segements
    converts              convertible debt landscape
    lev_loans             leveraged loan price landscape
        
    FUNCTIONS:    
    combine()             combine individual pricing landscapes
    ====================  ======================================================
    
    """

    def __init__(self):
        #
        Step.__init__(self, name = "credit capacity")
        self.asset_backed = Landscape("asset backed loans")
        self.bonds = None
        self.combined = None
        self.converts = None
        self.lev_loans = Landscape("leveraged loans")
        #bonds and converts should be a landscape in the future
        for obj in [self.asset_backed, self.lev_loans]:
            obj.relationships.set_parent(self)

    def combine(self):
        """


        CreditCapacity.combine() -> None


        Method combines multiple pricing landscapes into one. Starts with a
        blank landscape on every call. 
        """
        self.combined = Landscape()
        sources = [self.asset_backed, self.bonds, self.converts, self.lev_loans]
        market_segments = []
        for source in sources:
            if source:
                market_segments.append(source["size"])
        if len(market_segments) == 1:
            self.combined["size"] = copy.deepcopy(market_segments[0])
        else:
            by_size = self.combined.combine(market_segments,
                                            x_axis = "size",
                                            y_axis = "price")
            by_size = self.combined.label(by_size,
                                          x_axis = "size",
                                          y_axis = "price")
            self.combined["size"] = by_size
            #
            by_price = self.combined.pivot([by_size],
                                           x_axis = "price",
                                           y_axis = "size")
            by_price = self.combined.label(by_price,
                                           x_axis = "price",
                                           y_axis = "size")
            self.combined["price"] = by_price
        
                    
                
