# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.scenarios
"""

Module defines a class that represents arbitrarily rich BusinessUnit instances
as a collection of linked Excel worksheets.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Scenarios             class to hold scenario parameters for the model
====================  =========================================================
"""




# Imports
# n/a




# Constants
BASE = "base"
OTHERS = ["awesome", "good", "bad", "terrible"]

# Module Globals
# n/a

# Classes
class Scenarios(dict):
    """

    One tab per unit
    Children first
    Arbitrarily recursive (though should max out at sheet limit; alternatively,
    book should prohibit new sheets after that? or can have 2 limits: a soft
    limit where ModelChopper shifts into different representation mode, and a
    hard limit, where you just cant create any more sheets.)

    Most non-public methods force keyword-based arg entry to avoid potentially
    confusing erros (switching rows for columns, etc.)

    Methods generally leave current row pointing to their last completed
    (filled) row.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    original_entries      list; holds automatically included keys
    base                  property; return self[BASE] (base case scenario)

    FUNCTIONS:
    get_keys()            returns ordered list of keys
    update_base()         updates base case scenario with additional values
    ====================  =====================================================
    """

    def __init__(self, base=dict()):
        dict.__init__(self)

        self[BASE] = base

        self.original_entries = list()
        self.original_entries.append(BASE)

        for o in OTHERS:
            self[o] = dict()
            self.original_entries.append(o)

    @property
    def base(self):
        return self[BASE]

    def get_keys(self):
        """


        Scenarios.get_keys() -> list

        Method returns list of keys (scenario names) in instance, starting with
        those scenarios automatically included and ordering the remaining keys
        alphabetically.
        """
        result = self.original_entries
        for k in sorted(self.keys()):
            if k not in result:
                result.append(k)

        return result

    def update_base(self, new_values):
        """


        Scenarios.update_base() -> None

        --``new_values`` must be a dictionary containing values to add to
            the base case scenario

        Method updates base-case scenario dictionary with outside parameters.
        Method does NOT overwrite keys already in self.base/self[BASE].
        """
        for k in new_values.keys():
            if k not in self.base.keys():
                self.base[k] = new_values[k]
