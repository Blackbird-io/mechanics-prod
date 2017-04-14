#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.modelling.link
"""

Module defines Link class, which is a LineItem class specifically for path.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Link                  a LineItem with a pointer to a target business unit
====================  =========================================================
"""




# Imports
from .line_item import LineItem




# Constants
# n/a

# Classes
class Link(LineItem):
    """

    A Link is a LineItem that can have a target attribute.

    Link is a class specifically designed to be added to PATH to redirect
    focus to a target business unit.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    target                pointer to BusinessUnit where focus should be shifted

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    def __init__(self, target):
        if target:
            name = target.title
        else:
            name = None

        LineItem.__init__(self, name)
        self.target = target

    @classmethod
    def from_portal(cls, portal_data, statement):
        target = portal_data.pop('target')
        line_item = LineItem.from_portal(portal_data, statement)

        new = cls(None)
        new.__dict__.update(line_item.__dict__)
        new.target = target

        return new

    def to_portal(self, top_level=False):
        data = LineItem.to_portal(self, top_level=top_level)
        data['target'] = self.target.id.bbid
        data['link'] = True

        return data

