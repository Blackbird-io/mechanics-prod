#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.system.relationship
"""

Module defines Relationship class and provides certain related functions.

**NOTE: Class variables set at end of module (after class definition)**

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:

FUNCTIONS:

CLASSES:
Relationship          manages relationships between objects
====================  ==========================================================
"""




#  imports
from tools.parsing import deCase




# Constants
# n/a

# Classes
class Relationship:
    """
    This class handles relationships between objects, essentially forging links
    in a singly-linked list or tree. An instance of Relationship has a parent,
    but does not track its children. This class extracts some of the
    functionality formerly assigned to the Tags class.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    owner                 property; returns _owner of Relationship instance
    parent                property; returns _parent of instance's owner
    part_of               property; returns the name of parent or None

    FUNCTIONS:
    copy()                returns a copy of the object, preserving the parent
                          attribute
    set_parent()          sets non-public parent attribute _parent
    """

    def __init__(self, owner, parent=None):
        self._owner = owner
        self._parent = None
        self._level = None

        if parent:
            self.set_parent(parent)

    @property
    def level(self):
        # check to see that owner and parent are of same type before assigning
        # level, otherwise leave level as None.  If owner/parent of same type,
        # and parent does not yet have a level, assign zero
        if isinstance(self._parent, type(self._owner)):
            if self._parent.relationship.level is None:
                self._parent.relationship._level = 0

            self._level = self._parent.relationship.level + 1

        return self._level

    @property
    def owner(self):
        return self._owner

    @property
    def parent(self):
        return self._parent

    @property
    def part_of(self):
        if getattr(self.parent, "name", None):
            par_name = deCase(self.parent.name)
        else:
            #  parent doesn't have a name attribute or its name is None
            par_name = None

        return par_name

    def set_parent(self, parent):
        """


        Relationship.set_parent -> None

        Sets _parent non-public attribute to parent object
        """
        self._parent = parent

    def copy(self):
        """


        Relationship.copy -> obj

        Returns a new Relationship object with _parent attribute preserved
        """
        result = Relationship(self._owner, parent=self._parent)

        return result
