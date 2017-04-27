# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.round
"""

Module defines Round class
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Round                 Object representing information from a funding round
====================  ==========================================================
"""




# imports
# N/A




# Classes
class Round:
    """

    The Round class defines a round of investment. A Round can also be thought
    of as a class of shares ("Common Stock", "Series A", or "Options Pool").

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    name                  string
    id                    ID()
    size                  float, size of investment in dollars
    valuation             float, post money company valuation in dollars
    preference            float, liquidation preference

    FUNCTIONS:

    ====================  ======================================================
    """
    def __init__(self, name, size, valuation, preference=None):
        self.name = name
        self.size = size
        self.valuation = valuation
        self.preference = preference
        
    def to_portal(self):
        result = dict()
        result['name'] = self.name
        result['size'] = self.size
        result['valuation'] = self.valuation
        result['preference'] = self.preference
        
        return result
    
    @classmethod
    def from_portal(cls, data):
        name = data['name']
        size = float(data['size'])
        valuation = float(data['valuation'])
        preference = float(data['preference'])
        
        result = cls(name, size, valuation, preference)
        
        return result
