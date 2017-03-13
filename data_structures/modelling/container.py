# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2017
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.container
"""

Module defines Container class for objects with names and ids.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Container             class for organizing and storing objects
====================  ==========================================================
"""




# imports
import bb_exceptions

from data_structures.system.bbid import ID




# globals
# n/a


# classes
class Container:
    """

    The Container class provides organization and storage for objs.

    The main directory stores records of known objs by id.  The by_name
    directory maps obj names to ID's to enable easy lookup by name.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    directory             dict; holds objs keyed by BBID
    by_name               dict; maps obj name to BBID

    FUNCTIONS:
    add()                 adds a new obj
    copy()                returns a deep copy of self and all keys and objs
    get()                 retrieves a obj by id
    get_or_create()       retrieves or creates a obj matching provided info
    get_by_name()         retrieves a obj by name
    remove()              removes a obj by id
    ====================  ======================================================
    """

    def __init__(self):
        self.id = ID()
        self.directory = dict()
        self.by_name = dict()

    def add(self, obj):
        """


        Container.add() -> None

        --``obj`` is an instance of obj

        Method checks that obj has a valid name and ID and that these
        attributes do not conflict with existing entries before adding the
        new obj.
        """

        # Make sure this obj is valid
        if not obj.id.bbid:
            c = "Cannot add obj that does not have a valid bbid."
            raise bb_exceptions.IDError(c)

        if not obj.name:
            c = "Cannot add obj that does not have a valid name."
            raise bb_exceptions.BBAnalyticalError(c)

        if obj.id.bbid in self.directory:
            c = "Cannot overwrite existing obj. obj with id %s already" \
                " exists in directory." % obj.id.bbid.hex
            raise bb_exceptions.BBAnalyticalError(c)

        if obj.name in self.by_name:
            c = "Cannot overwrite existing obj. obj named %s already" \
                " exists in directory." % obj.name
            raise bb_exceptions.BBAnalyticalError(c)

        self.directory[obj.id.bbid] = obj
        self.by_name[obj.name.casefold()] = obj.id.bbid

    def copy(self):
        """


        Container.copy() -> Container

        Method returns a new Container instance. The items in the copy
        instance itself (tag : set of bbids) are identical to that of the
        original. The objs in the copy directory are copies of the objs
        in the original directory.
        """

        result = Container()

        for obj in self.directory.values():
            result.add_item(obj.copy())

        return result

    def get(self, bbid):
        """


        Container.get() -> obj or None

        --``bbid`` is a UUID corresponding to a obj

        Method returns obj with provided BBID or None.
        """
        result = None
        if bbid:
            result = self.directory.get(bbid, None)

        return result

    def get_by_name(self, name):
        """


        Container.get_by_name() -> obj or None

        --``name`` is the name of a obj

        Method uses provided name to search for and return a obj or None.
        """
        result = None
        bbid = self.by_name.get(name, None)
        if bbid:
            result = self.directory.get(bbid, None)
        return result

    def remove(self, bbid):
        """


        Container.remove() -> None

        Method removes obj with given BBID.
        """
        obj = self.directory.pop(id, None)
        if obj:
            self.by_name.pop(obj.name)
