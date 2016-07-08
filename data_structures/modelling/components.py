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

from data_structures.system.tags_mixin import TagsMixIn

from .components_base import ComponentsBase
from .equalities import Equalities




#globals
#n/a

#classes
class Components(ComponentsBase, TagsMixIn, Equalities):
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
    getOrdered()          legacy interface for get_ordered() 
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
        ComponentsBase.__init__(self)
        TagsMixIn.__init__(self, name)
        Equalities.__init__(self)

    def __eq__(self, comparator, trace = False, tab_width = 4):
        """


        Components.__eq__(comparator[, trace = False[, tab_width = 4]]) -> bool

        
        Call Equalities.__eq__ explicitly to bypass dict.__eq__ and support
        tracing.    
        """
        return Equalities.__eq__(self,comparator, trace, tab_width)

    def __ne__(self, comparator, trace = False, tab_width = 4):
        """


        Components.__ne__(comparator, [trace = False[, tab_width = 4]]) -> bool


        Explicit call to Equalities.__ne__ 
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)

    def copy(self):
        """


        Components.copy() -> Components


        Method returns a deep copy of components. Uses Tags.copy() to create a
        shell. Method then sets result.by_name to a blank dictionary and adds a
        copy of each unit in the instance to the result. 
        """
        result = ComponentsBase.copy(self)
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
        result = dict()
        for (bbid, bu) in self.items():
            if bu.life.alive:
                result[bbid] = bu
            else:
                continue
        #
        return result
    
    def getOrdered(self):
        """


        Components.getOrdered() -> list


        Legacy interface for components.get_ordered()
        """
        return self.get_ordered()

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
            pool = self.values()
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
