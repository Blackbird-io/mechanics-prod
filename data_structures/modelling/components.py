# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.components
"""

Module defines Components class, a container for business units.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Components            Tags-type container that stores business units
====================  ==========================================================
"""




#imports
import tools.for_tag_operations
import copy
import bb_exceptions
import bb_settings
import tools.for_printing as views
from data_structures.system.tags_mixin import TagsMixIn
from data_structures.system.relationships import Relationships
from .equalities import Equalities




#globals
#n/a

#classes
class Components(dict, TagsMixIn, Equalities):
    """

    The Components class defines a container that stores BusinessUnit objects
    keyed by their bbid. Components objects descend from the Tags class to
    support inheritance and extrapolation. Specifically, the tags on a
    Components instance, when maintained properly, should show whether any of
    the business units within that instance requires special extrapolation.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    by_name               dict; keys are unit names, values are unit bbids
    keyAttributes         list; CLASS; keep empty to follow standard dict logic
    relationships         instance of Relationships class

    FUNCTIONS:
    add_item()            adds an object to self, keyed under obj's bbid
    copy()                returns deep copy of instance and contents
    find_bbid()           return bbid that contains a known string
    get_all()             returns list of all units in instance
    get_living()          returns a bbid:bu dict of all bus that are alive
    get_ordered()         returns a list of values, ordered by key
    get_tagged()          return a dict of units with tags
    refresh_names()       clear and rebuild name-to-bbid dictionary
    remove_item()         remove an item from components
    ====================  ======================================================
    """
    #
    #while at first Components would seem to be a natural contender to use the
    #collections.ChainMap structure, the direction of information flow across
    #the Blackbird tree and the number of components create substantial
    #obstacles to semantically meaningful implementation.
    #

    keyAttributes = []
    #keyAttributes should remain an explicit empty list to maintain dictionary
    #comparison logic

    def __init__(self, name="Components"):
        dict.__init__(self)
        self.by_name = dict()
        self.relationships = Relationships(self)

        TagsMixIn.__init__(self, name)
        Equalities.__init__(self)

    def __str__(self, lines=None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls _get_pretty_lines() on instance.
        """
        if not lines:
            lines = views.view_as_components(self)
        line_end = "\n"
        result = line_end.join(lines)
        return result

    def __eq__(self, comparator, trace=False, tab_width=4):
        """


        Components.__eq__(comparator[, trace = False[, tab_width = 4]]) -> bool


        Call Equalities.__eq__ explicitly to bypass dict.__eq__ and support
        tracing.
        """
        return Equalities.__eq__(self, comparator, trace, tab_width)

    def __ne__(self, comparator, trace=False, tab_width=4):
        """


        Components.__ne__(comparator, [trace = False[, tab_width = 4]]) -> bool


        Explicit call to Equalities.__ne__
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    def copy(self):
        """


        Components.copy() -> Components


        Method returns a deep copy of components. Uses Tags.copy() to create a
        shell. Method then sets result.by_name to a blank dictionary and adds a
        copy of each unit in the instance to the result.
        """
        result = copy.copy(self)
        result.relationships = self.relationships.copy()

        # customize container
        result.clear()
        result.by_name = dict()

        # fill container (automatically add names)
        for unit in self.get_ordered():
            result.add_item(unit.copy())

        result.tags = self.tags.copy()

        return result

    def find_bbid(self, snippet):
        """


        Components.find_bbid(snippet) -> uuid


        Method returns first bbid in instance keys that contains the snippet.
        Snippet should be a string. Method returns None if no id in instance
        contains snippet.
        """
        result = None
        for bbid in self:
            if snippet in str(bbid):
                result = bbid
                break
            else:
                continue
        #
        return result

    def get_living(self):
        """


        Components.get_living() -> dict


        Method returns a dictionary by bbid of every object in instance that
        has life.alive == True.
        """
        from collections import OrderedDict

        result = OrderedDict()

        for (bbid, bu) in sorted(self.items()):
            if bu.life.alive:
                result[bbid] = bu
            else:
                continue
        #
        return result

    def get_ordered(self, order_by=None):
        """


        Components.get_ordered() -> list


        Method returns a list of every value in the instance, ordered by key.
        """
        result = []
        for k, bu in sorted(self.items(), key=order_by):
            result.append(bu)
        return result

    def get_all(self):
        """


        Components.get_all() -> list


        Method returns list of all units in instance; ordered if in DEBUG_MODE,
        unordered otherwise.
        """
        if bb_settings.DEBUG_MODE:
            # return ordered list
            result = []
            for k in sorted(self.keys()):
                result.append(self[k])
        else:
            result = list(self.values())

        return result

    def get_tagged(self, *tags, pool=None, recur=False):
        """


        Components.get_tagged() -> dict


        Return a dictionary of units (by bbid) that carry the specified tags.

        If ``pool`` is None, uses instance.values(). Delegates all selection
        work to tools.for_tag_operations.get_tagged()

        If ``recur`` is True, method runs recursively through all values in
        pool first, then adds in results from this level.
        """
        result = {}
        if not pool:
            pool = self.get_ordered()
        if recur:
            for bu in pool:
                one_down = bu.components.get_tagged(*tags, recur=recur)
                result.update(one_down)
        this_level = tools.for_tag_operations.get_tagged(pool, *tags)
        result.update(this_level)
        #
        return result

    def refresh_names(self):
        """


        Components.refresh_names() -> None


        Method clears and rebuilds the instance by_name dictionary for all units
        in instance.
        """
        self.by_name.clear()
        for bu in self.values():
            if bu.tags.name:
                self.by_name[bu.tags.name] = bu.id.bbid
            else:
                continue

    def refresh_ids(self):
        units = list(self.values())
        self.clear()
        self.by_name.clear()

        for unit in units:
            self[unit.id.bbid] = unit
            self.by_name[unit.name] = unit.id.bbid

    def add_item(self, bu):
        """


        Components.add_item() -> None

        --``bu`` is an instance of BusinessUnit or BusinessUnit object

        Method adds bu to the instance, keyed as bu.id.bbid. If bu does not
        specify a bbid, method raises IDError.

        Method also registers each unit's id under the unit's name in
        instance.by_name.
        """
        if not bu.id.bbid:
            c = "Cannot add a component that does not have a valid bbid."
            raise bb_exceptions.IDError(c)
        bu.relationships.set_parent(self)
        self[bu.id.bbid] = bu
        if bu.tags.name:
            self.by_name[bu.tags.name] = bu.id.bbid

    def remove_item(self, bbid):
        """


        Components.remove_item(bbid) -> BusinessUnit()


        Method removes an item from the components dictionary given it's bbid.
        Method then updates the by_name dictionary, and setPartOf -> None.
        Method returns the removed item (usually a BU)
        For Drivers, use Dr_Container.remove_driver() instead
        """
        bu = self.pop(bbid)
        bu.relationships.set_parent(None)
        if bu.tags.name:
            self.by_name.pop(bu.tags.name)

        return bu
