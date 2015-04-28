#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Components
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
import copy
import time
import BBExceptions
import BBGlobalVariables as Globals

from DataStructures.Platform.Tags import Tags

from .Equalities import Equalities




#globals
#n/a

#classes
class Components(dict, Tags, Equalities):
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

    FUNCTIONS:
    addItem()             adds an object to self, keyed under obj's bbid
    clearInheritedTags()  runs Tags method and then repeats for each component
    copy()                returns deep copy of instance and contents
    extrapolate_to()      delegates Tags.extrapolate_to()
    ex_to_default()       delegates to Tags.ex_to_default, which runs on copy()
    ex_to_special()       makes a shell, fills with items from seed & target
    getOrdered()          returns a list of values, ordered by key
    inheritTags()         runs default routine, then inherits from all comps
    refresh_names()       clear and rebuild name-to-bbid dictionary
    ====================  ======================================================
    """
    #
    #while at first Components would seem to be a natural contender to use the
    #collections.ChainMap structure, the direction of information flow across
    #the Blackbird tree and the number of components create substantial
    #obstacles to semantically meaningful implementation.
    #

    #
    keyAttributes = []
    #keyAttributes should remain an explicit empty list to maintain dictionary
    #comparison logic
    
    def __init__(self,name = "Components"):
        dict.__init__(self)
        Tags.__init__(self, name)
        Equalities.__init__(self)
        self.by_name = dict()

    def __eq__(self, comparator, trace = False, tab_width = 4):
        """

        Call Equalities.__eq__ explicitly to bypass dict.__eq__ and support
        tracing. 
        """
        return Equalities.__eq__(self,comparator, trace, tab_width)

    def __ne__(self, comparator, trace = False, tab_width = 4):
        """

        Explicit call to Equalities.__ne__ 
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)

    def addItem(self, bu):
        """


        Components.addItem(bu) -> None


        Method adds bu to the instance, keyed as bu.id.bbid. If bu does not
        specify a bbid, method raises IDError.

        Method also registers each unit's id under the unit's name in
        instance.by_name. 
        """
        if not bu.id.bbid:
            c = "Cannot add a component that does not have a valid bbid."
            raise BBExceptions.IDError(c)
        bu.setPartOf(self)
        self[bu.id.bbid] = bu
        if bu.name:
            self.by_name[bu.name] = bu.id.bbid

    def clearInheritedTags(self,recur = False):
        """


        Components.clearInheritedTags([recur = False]) -> None


        Method runs Tags.clearInheritedTags(). If recur == True, method then
        clears inherited tags for every component in self.getOrdered(). 
        """
        Tags.clearInheritedTags(self,recur)
        if recur:
            for C in self.getOrdered():
                C.clearInheritedTags(recur = True)

    def copy(self,enforce_rules = True):
        """


        Components.copy([enforce_rules = True]) -> Components


        Method returns a deep copy of components. Uses Tags.copy() to create a
        shell. Method then sets result.by_name to a blank dictionary and adds a
        copy of each unit in the instance to the result. 
        """
        result = Tags.copy(self, enforce_rules = True)
        #
        #customize container
        result.clear()
        result.by_name = dict()
        #
        #fill container (automatically add names)
        for C in self.getOrdered():
            rC = C.copy(enforce_rules)
            result.addItem(rC)
        return result

    def extrapolate_to(self,target):
        """


        Components.extrapolate_to(target) -> Components


        Method returns a new Components object that combines seed and target
        characteristics. Method delegates all work to Tags.extrapolate_to().
        """
        result = Tags.extrapolate_to(self,target)
        return result

    def ex_to_default(self,target):
        """


        Components.ex_to_default(target) -> Components


        Method returns a new Components object based primarily on the seed
        instance. Delegates work to Tags.ex_to_default().
        """
        result = Tags.ex_to_default(self,target)
        return result

    def ex_to_special(self,target):
        """


        Components.ex_to_special(target) -> Components


        Method returns a new Components object that combines seed and target
        characteristics.

        First, method generates an empty Components shell. The shell is a
        rules-enforced Tages.copy() of the seed instance that receives any
        extra tags from the target instance as well.

        Second, the method fills the shell with items from both seed and target.
        If an item appears in both (both seed and target have the same uuid
        key), the method extrapolates the seed item onto the target. Method
        copies shared items if they prohibited modification. Method then copies
        all seed- or target-specific items. 
        """
        #
        #step 1: make the container
        result = None
        #create shallow copies of seed and target to run tag and container
        #attribute inheritance without copying all of the contents
        alt_seed = copy.copy(self)
        #plain vanilla copy 
        alt_seed.clear()
        #empty Components instance, but with all the tags and other data
        result = alt_seed.copy(enforce_rules = True)
        result = Tags.ex_to_special(result,target,mode= "at")
        #updates result with those target tags it doesnt have already. "at" mode
        #picks up all tags from target. other attributes stay identical because
        #Tags uses a shallow copy.
        #
        #step 2: fill the container
        k_seed = set(seed.keys())
        k_target = set(target.keys())
        k_common = k_seed & k_target
        k_only_seed = k_seed - k_common
        k_only_target = k_target - k_common
        for k in k_only_seed:
            c_seed = seed[k]
            c_new = c_seed.copy(enforce_rules = True)
            result.addItem(c_new)
        for k in k_only_target:
            c_target = target[k]
            if self.checkOrdinary(c_target):
                continue
            else:
                #only add special items from target.
                c_new = c_target.copy(enforce_rules = False)
                result.addItem(c_new)
        for k in k_common:
            c_seed = seed[k]
            c_target = target[k]
            c_new = None
            if c_target.checkTouch():
                c_new = c_seed.extrapolate_to(c_target)
            else:
                c_new = c_target.copy(enforce_rules = False)
                #no "conceptual" movement, original and copy stay in the same
                #level in the same time period. 
            result.addItem(c_new)
        #
        #return result
        return result
        
    def getOrdered(self):
        """


        Components.getOrdered() -> list


        Method returns a list of every value in the instance, ordered by key. 
        """
        result = []
        for k in sorted(self.keys()):
            bu = self[k]
            result.append(bu)
        return result

    def inheritTags(self, recur = True):
        """


        Components.inheritTags([recur = True]) -> None


        Method provides a Components-specific form of tag inheritance compatible
        with the general inheritance interface.

        Method first runs Tags.inheritTags() on the instance. This step should
        generally should be a no-op because Components objects leave tagSources
        blank by default.

        Method then goes through every component in self.getOrdered() and
        inherits that component's tags.

        If ``recur`` == True, method asks each component to inheritTags() on its
        own before using that component as a source for the instance. 
        """
        Tags.inheritTags(self,recur)
        for bu in self.getOrdered():
            if bu:
                if recur:
                    bu.inheritTags()
                self.inheritTagsFrom(bu)

    def refresh_names(self):
        """


        Components.refresh_names() -> None


        Method clears and rebuilds the instance by_name dictionary for all units
        in instance. 
        """   
        self.by_name.clear()
        for bu in self.values:
            if bu.name:
                self.by_name[bu.name] = bu.id.bbid
            else:
                continue
        #
                
