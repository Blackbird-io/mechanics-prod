# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.business_unit
"""

Module defines BusinessUnit class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BusinessUnit          structured snapshot of a business at a given point in time
ParameterManager      manager class for unit parameters over time
====================  ==========================================================
"""




# Imports
# n/a




# Constants
# n/a

# Globals
# n/a

# Classes
class BusinessSudo:
    """

    Object describes a group of business activity. A business unit can be a
    store, a region, a product, a team, a relationship (or many relationships),
    etcetera.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:

    FUNCTIONS:
    ====================  ======================================================
    """
    # def __new__(cls, bu):
    #     return bu.copy()

    def __init__(self, bu, period):
        self.source_bu = bu#.copy()
        self.period = period
        self.id = bu.id
        self.xl = bu.xl
        self.tags = bu.tags
        self.life = bu.life.copy()
        self.components = bu.components
        self.complete = True
        self.periods_used = 1
        self.financials = bu.financials.copy()
        self.financials.relationships.set_parent(self)

    def _fit_to_period(self, *pargs, **kargs):
        return self.source_bu._fit_to_period(*pargs, **kargs)

    def _register_in_period(self, *pargs, **kargs):
        return self.source_bu._register_in_period(*pargs, **kargs)

    def reset_financials(self, *pargs, **kargs):
        return self.source_bu.reset_financials(*pargs, **kargs)

    def fill_out(self, *pargs, **kargs):
        return self.source_bu.fill_out(*pargs, **kargs)

    def copy(self, *pargs, **kargs):
        return self.source_bu.copy(*pargs, **kargs)
