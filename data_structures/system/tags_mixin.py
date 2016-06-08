# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.system.tags_mixin
"""

Module defines Relationship class and provides certain related functions.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
N/A

FUNCTIONS:
N/A

CLASSES:
TagsMixIn            mix-in class for Tags as component
====================  ==========================================================
"""




#  imports
from .tags import Tags




# Constants
# n/a

# Classes
class TagsMixIn:
    """
    This class is meant to be used as a mix-in for classes requiring tags
    functionality.  Class includes a "name" shortcut to tags.name

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    name                  property; name as stored in tags.required[0]

    FUNCTIONS:
    N/A
    """

    def __init__(self, name=None):
        self.tags = Tags(name)

    @property
    def name(self):
        return self.tags.name

    def set_name(self, new_name):
        """


        TagsMixIn.set_name() -> None

        --``new_name`` is the value to use for updating tags.name

        Method sets tags.name by delegating to tags.set_name().
        """
        self.tags.set_name(new_name)
