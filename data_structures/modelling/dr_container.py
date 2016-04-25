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

import bb_exceptions

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
    including a second dictionary called dr_directory.

    The main dictionary stores records of known drivers for each key. The keys
    are usually tags or line names. The records are a dictionary of position to
    driver bbid. 

    The directory stores driver objects keyed by bbid. When a client needs to
    access the actual drivers for a given line, she calls the get_drivers()
    method for the line name. This container then delivers a list of drivers
    in order of increasing position.

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
    add_item()             adds bbid for applicable tags, object to directory
    clearInheritedTags()  clears own tags and optionally those of all drivers
    copy()                returns a deep copy of self and all keys and drivers
    ex_to_special()       returns a new DrContainer that combines seed & target
    get_drivers()         returns a list of drivers associated with a tag
    get_ordered()         returns a list of all drivers sorted by bbid
    inheritTags()         inherits tags from a list of all drivers in instance
    remove_driver()       remove a driver from this driver container
    setPartOf()           sets parentObject for instance **and** drivers
    ====================  ======================================================
    """
    
    def __init__(self,name = "DrContainer"):
        Components.__init__(self,name)
        self[None] = set()
        self.dr_blank = Driver()
        self.dr_directory = {}        

    def add_item(self, new_driver, *other_keys):
        """


        DrContainer.addItem(newDriver, *otherKeys) -> None


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
        if not self.parentObject:
            c = "Cannot add driver. DrContainer does not have a parent object."
            raise bb_exceptions.IOPMechanicalError(c)
        
        if not new_driver.id.bbid:
            c = "Cannot add driver that does not have a valid bbid."
            raise bb_exceptions.IDError(c)

        # Could prohibit implicit overwrites, but would be cumbersome. Would
        # have to check whether a bbid is already in a given key's set.

        new_driver.setPartOf(self.parentObject)
        # Drivers point to business unit as a parent object.
        self.dr_directory[new_driver.id.bbid] = new_driver

        # Build the set of keys where we are going to register the driver
        keys = set()
        for trigger_tags in new_driver.workConditions.values():
            keys = keys | set(trigger_tags)
        keys = keys | set(other_keys)
        # Stip out muck
        keys = keys - {None}
        keys = keys - set(self.dr_blank.workConditions["name"])
        #  driver.workConditions[x] == "FAIL" by default

        applied_keys = {key.casefold() for key in keys}
        
        for decased_key in applied_keys:
            record = self.setdefault(decased_key, dict())
            if new_driver.position in record:
                c = "A single record can only have one driver with a given position."
                c += "\n position %s already exists for key ``%s``"
                c = c % (new_driver.position, decased_key)
                c += "\n unable to insert driver ``%s``"
                c = c % new_driver.name
                #
                for num, item in enumerate(self.items()):
                    print(num, " ", item, "\n")
                print()
                print(self[decased_key])
                raise Exception(c)
            else:
                record[new_driver.position] = new_driver.id.bbid        
   
    def clearInheritedTags(self, recur=False):
        """


        DrContainer.clearInheritedTags([recur=False]) -> None


        Method runs Tags.clearInheritedTags() on the instance, then has the
        instance , then clears inherited tags 
        """
        Tags.clearInheritedTags(self,recur)
        for dr in self.dr_directory.items():
            dr.clearInheritedTags(recur)
            
    def copy(self, enforce_rules=True):
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
        # Make container
        result = Tags.copy(self, enforce_rules)
        result.clear()
        result.dr_directory = {}
        # Make a clean empty dictionary for new directory
        #
        # Configure and fill the container
        result.dr_blank = self.dr_blank.copy(enforce_rules=False)
        
        for (k, position_dict) in self.items():
            result[k] = position_dict.copy()
            # Set-specific copy; new set of same bbids

        for (bbid,dr) in self.dr_directory.items():
            result.dr_directory[bbid] = dr.copy(enforce_rules)
        #
        # Return 
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
        #in main storage, ks are tags or names; values are dicts of position
        seed_ks = set(seed.keys())
        target_ks = set(target.keys())
        #
        shared_ks = seed_ks & target_ks
        seed_only_ks = seed_ks - shared_ks
        target_only_ks = target_ks - shared_ks
        #        
        for line_name in seed_only_ks:
            result[line_name] = seed[line_name].copy()
            # Copy the {position:bbid} record wholesale.
        #
        for line_name in shared_ks:
            result[line_name] = dict()
            for position, bbid in target[line_name].items():
                if bbid in result.dr_directory:
                    result[line_name][position] = bbid
                else:
                    continue
            result[line_name].update(seed[line_name])
            
            #to the extent the target set for a given tag includes any bbids
            #that are not in the seed, those bbids should only go in if they
            #are associated with a special driver. the directory integration in
            #2a picked up all special drivers from target, so now can judge
            #whether a target-only driver is special by checking whether that
            #driver's id is in result.dr_directory. no need to get the driver
            #itself - if it was ordinary and located only in the target, it
            #would not have made it in to the directory.

        # Upgrade-S: Can get the intersection of the bbid values in each line
        # record and the drivers we carry over. Then only add those. Requires
        # flipping the dict to val:k. Unclear if you can do that quickly. 

        for line_name in target_only_ks:
            for position, bbid in target.items():
                if bbid in result.dr_directory:
                    record = result.setdefault(line_name, dict())
                    record[position] = bbid
                else:
                    continue
        # For ids that appear only in the target, discard those we didn't
        # include in the directory, keep others.
    
        # Step 3: return container
        return result               
    
    def get_drivers(self, tag):
        """


        DrContainer.get_drivers() -> list


        Method returns a list of drivers associated with the tag, ordered by
        driver bbid.
        """
        result = []
        available = self[tag]
        # ``available`` is a int:bbid dictionary
        
        for position, bbid in sorted(available.items()):
            # Lambda may be faster here, not using for clarity
            bbid = available[position]
            driver = self.dr_directory[bbid]
            result.append(driver)

        return result

    def get_ordered(self):
        """


        DrContainer.get_ordered() -> set()


        Method returns a list of all drivers contained in instance sorted by
        driver.id.bbid.
        """
        result = []
        for bbid in sorted(self.dr_directory.keys()):
            dr = self.dr_directory[bbid]
            result.append(dr)
        return result

    def inheritTags(self, recur=True):
        """


        DrContainer.inheritTags([recur = True]) -> None


        Method runs Tags.inheritTags() on the instance, then has the instance
        inherit tags directly from every driver it contains (via .getOrdered()).
        """
        Tags.inheritTags(self, recur)
        for dr in self.get_ordered():
            self.inheritTagsFrom(dr, recur)
        # In tag inheritance, order is significant. Want to inherit tags in the
        # same order every time. 

    def remove_driver(self, line_name_key):
        """


        DrContainer.remove_driver(line_name_key) -> None


        Method removes all drivers with specified line_name_key.
        Note that DrContainer's dictionary keys are all line names,
        which come from Driver.workConditions['line_name']
        """
        dr_list = self.get_drivers(line_name_key)
        for dr in dr_list:
            # Remove from dr_directory dictionary
            bbid = dr.id.bbid
            del(self.dr_directory[bbid])
            # Remove from DrContainer dictionary
            del(self[line_name_key])

    def setPartOf(self, parentObj, recur=True):
        """


        DrContainer.setPartOf(parentObj,recur = True) -> None


        Method runs Tags.setPartOf() on the instance, and, if ``recur`` is True,
        all drivers in the instance. 
        """
        Tags.setPartOf(self,parentObj)
        if recur:
            for dr in self.dr_directory.values():
                dr.setPartOf(parentObj)
