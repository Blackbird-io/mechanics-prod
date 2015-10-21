#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.dr_container
"""

Module defines DriversContainer class, a Components-type container for Driver
objects. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
DriversContainer      subclass of Components
====================  ==========================================================
"""




#imports
import copy
from operator import attrgetter

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.system.tags import Tags

from .components import Components
from .driver import Driver




#globals
#n/a

#classes
class DrContainer(Components):
    """ 

    The DrContainer class provides organization and storage for drivers that
    work on a particular business unit.

    Each instance is a Components-type dictionary with supplemental attributes,
    including a second dictionary called dr_directory. The main dictionary
    stores sets of driver bbids associated with a particular lineItem name or
    tag, keyed by the tag.

    The directory stores driver objects keyed by bbid. When a client needs to
    access the actual drivers for a given line, she calls the getDrivers()
    method for the line name.

    The class configures drivers to point to the DrContainer's parent business
    unit as the driver's own parent. This hook makes it easier for drivers to
    work on the parent.

    NOTE: Equivalence (``==``) operations on DrContainers run through
    dict.__eq__ and compare only the main content (keys and sets of bbids), not
    the actual driver objects associated with those bbids. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    
    DATA:
    dr_blank              empty Driver() object for checking driver registration
    dr_directory          dictionary of bbid:driver objects
    
    FUNCTIONS:
    addItem()             adds bbid for applicable tags, object to directory
    clearInheritedTags()  clears own tags and optionally those of all drivers
    copy()                returns a deep copy of self and all keys and drivers
    ex_to_special()       returns a new DrContainer that combines seed & target
    getDrivers()          returns a list of drivers associated with a tag
    getOrdered()          returns a list of all drivers sorted by bbid
    get_tagged()          returns a dict of drivers with tags
    inheritTags()         inherits tags from a list of all drivers in instance
    setPartOf()           sets parentObject for instance **and** drivers
    ====================  ======================================================
    """
    
    def __init__(self,name = "DrContainer"):
        Components.__init__(self,name)
        self[None] = set()
        self.dr_blank = Driver()
        self.dr_directory = {}        

    def addItem(self,newDriver,*otherKeys):
        """


        DrContainer.addItem(newDriver,*otherKeys) -> None


        Method creates sets of bbids for drivers associated with a specific tag.
        
        Method registers the driver's bbid under the driver's
        workConditons["name"] and ["allTags"] keys. Method will skip
        registration for a workConditions key if that workCondition is empty
        (e.g, ``[None]``) or equivalent to that of the dummy blank driver on the
        instance. Method then also registers the driver under every key provided
        as part of the ``otherKeys`` argument.

        Method also adds the driver to the instance's dr_directory.
        
        Upon registration, Method updates driver's parentObject attribute to
        point to the instance's parentObject (ie, the business unit housing this
        particular DrContainer).

        NOTE: Method will overwrite old versions of a driver with new versions.
        """
        #
        if not self.parentObject:
            c = "Cannot add driver. DrContainer does not have a parent object."
            raise BBExceptions.IOPMechanicalError(c)
        if not newDriver.id.bbid:
            c = "Cannot add driver that does not have a valid bbid."
            raise BBExceptions.IDError(c)
        #Could prohibit implicit overwrites, but cumbersome: would have to check
        #whether a bbid is already in a given key's set.
        #
        newDriver.setPartOf(self.parentObject)
        #Drivers point to the business unit as parent object
        self.dr_directory[newDriver.id.bbid] = newDriver
        #
        keys = set()
        l_blank = [None]
        dr_wcName = newDriver.workConditions["name"]
        default_wcName = self.dr_blank.workConditions["name"]
        dr_wcTags = newDriver.workConditions["allTags"]
        default_wcTags = self.dr_blank.workConditions["allTags"]
        #incrementally build up keys relevant to this driver
        #``|`` is the set.union() operation
        if dr_wcName != l_blank and dr_wcName != default_wcName:
            keys = keys | set(dr_wcName)
        if dr_wcTags != l_blank and dr_wcName != default_wcTags:
            keys = keys | set(dr_wcTags)
        if otherKeys != tuple():
            keys = keys | set(otherKeys)
        for k in keys.copy():
            #iterate through copy because going to change the set
            if k:
                keys.add(k.casefold())
        keys_existing = keys & set(self.keys())
        keys_new = keys - keys_existing
        for k in keys_existing:
            self[k].add(newDriver.id.bbid)
        for k in keys_new:
            self[k] = {newDriver.id.bbid}
   
    def clearInheritedTags(self,recur = False):
        """


        DrContainer.clearInheritedTags([recur=False]) -> None


        Method runs Tags.clearInheritedTags() on the instance, then has the
        instance , then clears inherited tags 
        """
        Tags.clearInheritedTags(self,recur)
        for dr in self.getOrdered():
            dr.clearInheritedTags(recur)
            
    def copy(self, enforce_rules = True):
        """


        DrContainer.copy([enforce_rules = True]) -> DrContainer


        Method returns a new DrContainer instance. The items in the copy
        instance itself (tag : set of bbids) are identical to that of the
        original. The drivers in the copy directory are copies of the drivers in
        the original directory.

        ``enforce_rules`` toggles whether driver copies in the copy.dr_directory
        comply with any applicable tag rules. 
        """
        #
        #make container
        result = Tags.copy(self,enforce_rules)
        result.clear()
        result.dr_directory = {}
        #make a clean empty dictionary for new directory
        #
        #configure and fill the container
        result.dr_blank = self.dr_blank.copy(enforce_rules = False)
        for (k, bbid_set) in self.items():
            result[k] = bbid_set.copy()
            #set-specific copy; new set of same bbids
        for (bbid,dr) in self.dr_directory.items():
            result.dr_directory[bbid] = dr.copy(enforce_rules)
        #
        #return 
        return result
        
    def ex_to_special(self,target):
        """


        DrContainer.ex_to_special(target) -> DrContainer


        Method returns a new DrContainer with a blend of seed and target data.

        The directory in the new DrContainer includes copies of all drivers
        exclusive to the seed; extrapolations of any drivers shared by the two
        objects; and copies of any **special** drivers exclusive to the target.
        If a target version of a shared driver prohibits modification, the
        method includes a copy (rather than an extrapolation) of that driver.

        The method leaves ordinary drivers exclusive to the target out of the
        result directory.

        NOTE: Extrapolating one driver to another runs through Tags and returns
        Driver.copy() copies of either the seed or the target, depending on the
        circumstances. 

        After putting together the result directory, the method moves on to main
        storage. Here, for tag/name keys and bbid-set values stored in the
        instance itself, the method again picks up all entries from seed. The
        method supplements these, either by adding bbids to a known key or
        adding a key:value entry, with those bbids in target that point toward
        special drivers. 
        """
        #
        #step 1: make container
        seed = self
        alt_seed = copy.copy(seed)
        alt_seed.clear()
        alt_seed.dr_directory = {}
        result = alt_seed.copy(seed,enforce_rules = True)
        #deep copy of self, but without any drivers; picks up any class-specifc
        #attribute copying rules.
        result = Tags.ex_to_special(result,target,mode = "at")
        #updates result with those target tags it doesnt have already. "at" mode
        #picks up all tags from target. other attributes stay identical because
        #Tags uses a shallow copy.
        #
        #step 2: fill container
        #2a: start with dr_directory
        seed_ids = set(seed.dr_directory.keys())
        target_ids = set(target.dr_directory.keys())
        shared_ids = seed_ids & target_ids
        seed_only_ids = seed_ids - shared_ids
        target_only_ids = target_ids - shared_ids
        for bbid in seed_only_ids:
            s_dr = seed.dr_directory[bbid]
            new_dr = s_dr.copy(enforce_rules = True)
            result.dr_directory[bbid] = new_dr
        for bbid in shared_ids:
            s_dr = seed.dr_directory[bbid]
            t_dr = target.dr_directory[bbid]
            if self.checkTouch(t_dr):
                #call self.checkTouch() on t_dr instead of t_dr.checkTouch() to
                #make sure method applies most recent standards for do-not-touch
                #status. t_dr could have an outdated criteria. 
                new_dr = s_dr.extrapolate_to(t_dr)
            else:
                #target version of the driver is tagged hands off, copy it
                #wholesale
                new_dr = t_dr.copy(enforce_rules = False)
            result.dr_directory[bbid] = new_dr
        for bbid in target_only_ids:
            t_dr = target.dr_directory[bbid]
            if self.checkOrdinary(t_dr):
                continue
            else:
                #driver is special
                new_dr = t_dr.copy(enforce_rules = False)
                result.dr_directory[bbid] = new_dr
        #dr_directory filled out
        #2b: now work on main storage
        #in main storage, ks are tags or names; values are sets of bbids
        seed_ks = set(seed.keys())
        target_ks = set(target.keys())
        shared_ks = seed_ks & target_ks
        seed_only_ks = seed_ks - shared_ks
        target_only_ks = target_ks - shared_ks
        for k in seed_only_ks:
            result[k] = seed[k].copy()
        for k in shared_ks:
            result[k] = seed[k].copy()
            target_additions = target[k] - seed[k]
            if target_additions:
                for bbid in target_additions:
                    if bbid in result.dr_directory:
                        result[k].add(bbid)
                    else:
                        continue
            #to the extent the target set for a given tag includes any bbids
            #that are not in the seed, those bbids should only go in if they
            #are associated with a special driver. the directory integration in
            #2a picked up all special drivers from target, so now can judge
            #whether a target-only driver is special by checking whether that
            #driver's id is in result.dr_directory. no need to get the driver
            #itself - if it was ordinary and located only in the target, it
            #would not have made it in to the directory. 
        for k in target_only_ks:
            for bbid in target[k]:
                if bbid in result.dr_directory:
                    if k in result:
                        result[k].add(bbid)
                    else:
                        result[k] = {bbid}
                else:
                    continue
        #
        #step 3: return container
        return result               
    
    def getDrivers(self,tag):
        """


        DrContainer.getDrivers(tag) -> list


        Method returns a list of drivers associated with the tag, ordered by
        driver bbid.
        """
        result = []
        dr_ids = self[tag]
        for bbid in sorted(dr_ids):
            dr = self.dr_directory[bbid]
            result.append(dr)
        return result

    def getOrdered(self):
        """


        DrContainer.getOrdered() -> set()


        Method returns a list of all drivers contained in instance sorted by
        driver.id.bbid.
        """
        result = []
        for bbid in sorted(self.dr_directory.keys()):
            dr = self.dr_directory[bbid]
            result.append(dr)
        return result
    
    def get_tagged(self, *tags, pool = None):
        """


        DrContainer.get_tagged(*tags[, pool = None]) -> dict


        Return a dictionary of objs (by bbid) that carry the specified tags. 
        If ``pool`` is None, uses values from instance.dr_directory. Delegates
        all work to Components.get_tagged().
        """
        if not pool:
            pool = self.dr_directory.values()
        result = Components.get_tagged(self, *tags, pool = pool)
        #
        return result

    def inheritTags(self, recur = True):
        """


        DrContainer.inheritTags([recur = True]) -> None


        Method runs Tags.inheritTags() on the instance, then has the instance
        inherit tags directly from every driver it contains (via .getOrdered()).
        """
        Tags.inheritTags(self,recur)
        for dr in self.getOrdered():
            self.inheritTagsFrom(dr,recur)

    def setPartOf(self,parentObj,recur = True):
        """


        DrContainer.setPartOf(parentObj,recur = True) -> None


        Method runs Tags.setPartOf() on the instance, and, if ``recur`` is True,
        all drivers in the instance. 
        """
        Tags.setPartOf(self,parentObj)
        if recur:
            for dr in self.getOrdered():
                dr.setPartOf(parentObj)
