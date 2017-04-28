# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.record
"""

Module defines Record class
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Record                Object representing information from a funding record
====================  ==========================================================
"""



import bb_exceptions
from data_structures.system.bbid import ID




class Record:
    """

    The Record class defines a record of cash investment in exchange for shares

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    owner_name            string, name of investor or employee who owns shares
    round_name            string, name of round or class of shares
    units                 float, number of shares or options
    cash                  float, amount of cash invested to buy shares

    FUNCTIONS:

    ====================  ======================================================
    """
    def __init__(self, owner_name, round_name, units, cash):
        self.owner_name = owner_name
        self.round_name = round_name
        self.units = units
        self.cash = cash
    
    def to_database(self):
        result = dict()
        result['owner_name'] = self.owner_name
        result['round_name'] = self.round_name
        result['units'] = self.units
        result['cash'] = self.cash
        
        return result

    @classmethod
    def from_database(cls, data):
        owner_name = data['owner_name']
        round_name = data['round_name']
        units = float(data['units'])
        cash = float(data['cash'])

        result = cls(owner_name, round_name, units, cash)

        return result
