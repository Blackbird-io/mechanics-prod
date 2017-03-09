# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.formula
"""

Module defines Formula class. Formula objects provide a lattice for holding and
identifying work functions in the FormulaCatalog.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Formula               placeholder for formula functions from content modules
====================  ==========================================================
"""




#imports
from data_structures.system.bbid import ID
from data_structures.system.tags import Tags
from data_structures.system.tags_mixin import TagsMixIn




#globals
#n/a

#classes
class Formula(TagsMixIn):
    """
    Formula objects provide a lattice for identifying, tagging, and storing
    work functions in the formula catalog.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    func                  placeholder for formula function from content module
    id                    instance of Platform.ID.ID class
    source                relative path of conent module that described obj
    tags                  instance of Platform.Tags class

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self, name=None):
        TagsMixIn.__init__(self, name=name)
        self.func = None
        self.id = ID()
        self.source = None
