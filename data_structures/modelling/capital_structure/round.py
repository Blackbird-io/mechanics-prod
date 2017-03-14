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



from data_structures.system.bbid import ID




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
        self.id = ID()
        self.size = size
        self.valuation = valuation
        self.preference = preference
        # self.date = date


