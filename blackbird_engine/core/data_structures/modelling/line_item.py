#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.line_item
"""

Module defines LineItem class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LineItem              storage for numerical values and tags
====================  ==========================================================
"""




# Imports
import copy
import time

import bb_exceptions
import tools.for_printing as printing_tools

from data_structures.guidance.guide import Guide
from data_structures.system.tags import Tags

from .equalities import Equalities
from ._new_statement import Statement




# Constants
T_CONSOLIDATED = Tags.tagManager.catalog["consolidated"]

# Classes
class LineItem(Statement):
    """
    

    Instances of this class become components of a BusinessUnit.Financials list.

    A lineitem's value should be specified through setValue(). setValue()
    requires a signature. Values specified at instance construction get signed
    by LineItem.__init__(). Some methods may decline to sign a lineitem. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    guide                 instance of Guide object
    keyAttributes         list, CLASS, parameters for comparison by Equalities
    log            list of (signature,time,value) tuples
    value
    
    FUNCTIONS:
    clear()               if modification permitted, sets value to None
    copy()                returns a new line w copies of key attributes
    extrapolate_to()      delegates to Tags.extrapolate_to()
    ex_to_default()       returns a Line.copy() of self w target parentObject
    ex_to_special()       delegates to Tags.ex_to_special()
    pre_format()          make the ``formatted`` string
    replicate()           make a copy and fix line name
    setValue()            sets value to input, records signature
    toggleSign()          change sign to 0 or 1
    ====================  ======================================================
    """
    keyAttributes = Statement.keyAttributes + ["value", "requiredTags", "optionalTags"]

##    LineItem object currently runs on defined (``keyAttribute``) comparisons;
##    if using comprehensive attribute comparisons instead, make sure to specify
##    parentObject as an irrelevantAttribute. Otherwise, comparisons will loop:
##    the parentObj may itself have an __eq__ method that points back to this
##    lineItem. See Equalities docs for more info.
    
    SIGNATURE_FOR_CREATION = "__init__"
    SIGNATURE_FOR_VALUE_RESET = "LineItem.resetValue"
    SIGNATURE_FOR_DEFAULT_EXTRAPOLATION = "LineItem.ex_to_default"
    SIGNATURE_FOR_SPECIAL_EXTRAPOLATION = "LineItem.ex_to_special"
    SIGNATURE_FOR_REPLICA_MANAGEMENT = "Bringing down value."
    SIGNATURE_FOR_INCREMENTATION = "Incremented "

    SUMMARY_PREFIX = "total "

    TAB_WIDTH = 2
    
    def __init__(self, name=None, value=None):
        Statement.__init__(self, name)

        self._local_value = None
        
        self.guide = Guide()
        self.log = []
        self.position = None
        if value is not None:
            # BU.consolidate() will NOT increment items with value==None. On the
            # other hand, BU.consolidate() will increment items with value == 0.
            # Once consolidate() changes a lineitem, derive() will skip it. To
            # allow derivation of empty lineitems, must start w value==None.
            self.set_value(value, self.SIGNATURE_FOR_CREATION)

    # Lines can contain a mutable set of details, so we don't include a hash
    # method. Since it's difficult to compare lines to each other unless you
    # know exactly what the user has in mind, we don't support set operations
    # out of the box. Otherwise, you might get a response that a line is "in"
    # a particular set that actually contains an instance with the
    # same value but very different details. 
                                  
    def __str__(self):
        result = "\n".join(self._get_line_strings())
        result += "\n"
        return result

        # Now at the top, you print the lines and they look normal
        # but at the level of each line you have recursion and extra tabs
    
    def clear(self):
        """


        L.clear() -> None


        Method sets self.value to None by running L.setValue() with the value
        override. Method also sets the instance's sign to positive.

        NOTE: Method is a no-op for instances that do not pass checkTouch()
        Tags.checkTouch() returns False if the instance has tags that completely
        prohibit modification.
        """
        if self.checkTouch():
            if self.details:
                self._bring_down_local_value()
                Statement.reset(self)

            else:
                sig = self.SIGNATURE_FOR_VALUE_RESET
                self.set_value(None, sig, override=True)
                                              
        #<-----------------------------------------------------------------------------------may want to raise error #<-------------------------------redo this here
            # if you are trying to clear a hard-coded value, unless force=True
            
    def copy(self, enforce_rules=True):
        """


        Line.copy() -> Line


        Method returns a copy of the instance. Uses Tags.copy() to generate a
        shallow copy with independent tags objects. If enforce_rules is True,
        copy conforms to ``out`` rules.
        """
        new_line = Statement.copy(self, enforce_rules)
        # Statement method picks up details, _local_value, and tags
        new_line.guide = copy.deepcopy(self.guide)
        new_line.log = self.log[:]

        return new_line

##        new_line = Tags.copy(self, enforce_rules)
##        new_line.details = self.details.copy()
##        new_line.guide = copy.deepcopy(self.guide)
##        new_line.log = self.log[:] #<-------------------------------------------------------can add a line that we copied
##
##        return new_line

    def extrapolate_to(self, target):
        """


        LineItem.extrapolate_to() -> LineItem


        Method extrapolates instance characteristics to target and returns a
        new object that combines both.

        NOTE: Method delegates all work to Tags.extrapolate_to (standard
        subroutine selection logic).
        """
        result = Tags.extrapolate_to(self, target)
        return result

    def ex_to_default(self, target):
        """


        Line.ex_to_default() -> Line


        Method creates a LineItem.copy() of instance. Method signs copy with
        extrapolation signature if copy.modifiedBy() doesn't already end with
        one.

        Copy continues to point to seed parentObject.
        """
        #basic behavior: copy instance, set to seed.parentObject, if any
        result = self.copy(enforce_rules=True)
        
        ex_d_sig = self.SIGNATURE_FOR_DEFAULT_EXTRAPOLATION

        if ex_d_sig not in result.log[-1]:
            r_val = result.value
            result.set_value(r_val, ex_d_sig)
            
        return result

    def ex_to_special(self,target):
        """


        LineItem.ex_to_special() -> LineItem


        Method delegates all work to Tags.ex_to_special.

        Special extrapolation for LineItems returns a LineItem.copy of seed
        updated with new tags from the target. Method signs the result unless
        modifiedBy already ends with its signature.
        """
        result = Tags.ex_to_special(self,target)
        
        ex_s_sig = self.SIGNATURE_FOR_SPECIAL_EXTRAPOLATION

        if ex_s_sig not in result.log[-1]:
            r_val = result.value
            result.setValue(r_val,ex_s_sig)
        return result        
      
    def setValue(self, value, signature,
                 overrideValueManagement=False):
        """


        L.setValue() -> None


        **LEGACY INTERFACE**

        Use set_value() instead.
        """
        return self.set_value(value, signature, overrideValueManagement)
            
    def set_value(self, value, signature, override=False):
        """


        Line.set_value() -> None


        Set line value, add entry to log. Value must be numeric unless
        ``override`` is True. 
        """
        if not override:
            test = value + 1
            # Will throw exception if value doesn't support arithmetic
            
        self._local_value = value
        log_entry = (signature, time.time(), value)
        self.log.append(log_entry)
    
    @property
    def value(self):
        """
        read-only property
        """
        result = None

        if not self.details:
            result = self._local_value

        else:
            if self._local_value:
                self._bring_down_local_value()

            result = self._sum_details()
                    
        return result
                                    
    def increment(self, matching_line, signature=None, consolidating=False):
        """


        Line.increment() -> None


        Increment line value by matching line and details. If ``consolidating``
        is True, 
        """
        if matching_line.value is None:
            pass

        else:
            if matching_line.details:
                Statement.increment(self, matching_line, consolidating=consolidating)
                # Use Statement method here because we are treating the matching
                # line as a Statement too. We assume that its details represent
                # all of its value data. Statement.increment() will copy those
                # details to this instance. 
        
            else:
                if signature is None:
                    signature = self.SIGNATURE_FOR_INCREMENTATION

                starting_value = self.value or 0            
                new_value = starting_value + matching_line.value
                
                self.set_value(new_value, signature)
            
                if consolidating:
                    self.inheritTagsFrom(matching_line)
                    self.tag(T_CONSOLIDATED)
                    #<-------------------------------------------------------------------------------------------------------check when im supposed to inherit tags
        #

    #
    #go through basic cases: adding 2 lines with 2 details each
    # the details from the bottom (C, D) should get the consolidated tag
    # the details from the top should not
    
    # Once we tag the instance with "consolidate", we will no longer try
    # to write to its value. But can still write to its details.
    # So need to make sure that replica is also tagged consolidate
        #but presumably we will tag replica when the recursion gets to it
        #if replica is tagged consolidate... then parent can no longer get a derivation
            #and should also be tagged consolidate #<------------------------------------------------------------------------------
            #<-------is this even the right pattern? can have superimposition: pick up from below, plus add local results
                    #vs requiring the activity to take place in a separate "operating" unit

    #new approach to derive:
        #a. get all ordered(): generate a full list
            #generate complete list:
                #for line in self:
                    #if line.details:
                        #result.extend(line.get_complete_list())
                    #else:
                        #result.append(line)
    
        #b. walk through incrementally:
            #def derive_line():
                #if line.details:
                    #for detail in line.get_ordered():
                        #self.derive(detail)
                #else:
                    #basic derive routine   
            
    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _bring_down_local_value(self):
        """


        Line._bring_down_local_value() -> None


        Bring down instance's local value to replica. No-op if local value is
        None.
        """
        if self._local_value is None:
            pass

        else:
            replica = self._get_replica()
            sig = self.SIGNATURE_FOR_REPLICA_MANAGEMENT
                                          
            if replica:
                # Replica already exists, so it must have a non-None value. We
                # also know that instance has a non-None value, otherwise we
                # would be in the no-op block.
                new_value = replica.value + self._local_value
                replica.set_value(new_value, sig)
                replica.inheritTagsFrom(self)

            else:
                self._make_replica()
                # New replica will come with existing local value

            self.set_value(None, sig, override=True)

##    def _get_line_strings_old(self, prefix=""):
##        """
##        -> list
##
##        Return list of formatted strings for instance and any details. 
##        """
##        result = []
##        if self.details:
##            header = prefix + printing_tools.format_as_line(self, header=True)
##            result.append(header)
##
##            detail_indent = prefix + "\t"
##            for line in self.get_ordered():
##                
##                view = line._get_line_strings(prefix=detail_indent)
##                result.extend(view)
##
##            footer = prefix + printing_tools.format_as_line(self, prefix=self.SUMMARY_PREFIX) #<-------------------- should have format_as_footer and format_as_header() methods
##            result.append(footer)
##                                
##        else:
##            basic = prefix + printing_tools.format_as_line(self)
##            result.append(basic)
##
##        return result

    def _get_line_strings(self, indent=TAB_WIDTH):
        """
        -> list

        Return list of one or more strings that describe this line and any
        details. Lines have raw ends. 
        """

        result = []
        
        if not self.details:
            # Simple view: only the local value
            simple = printing_tools.format_as_line(self, left_tab=indent)
            result.append(simple)
        else:
            # Detailed view: when this line has details
            header = printing_tools.format_as_line(self, header=True, left_tab=indent)
            result.append(header)

            extra_tab = indent + self.TAB_WIDTH
            for detail in self.get_ordered():
                view = detail._get_line_strings(extra_tab)
                # Will always return a list of strings
                result.extend(view)

            footer = printing_tools.format_as_line(self, prefix=self.SUMMARY_PREFIX, left_tab=indent)
            result.append(footer)

        return result
    
    def _get_replica(self):
        """

        -> Line
        """
        replica = self.details.get(self.name)
        return replica

    def _make_replica(self):
        """

        -> None
        """
        replica = Tags.copy(self, enforce_rules=False)                                      
        replica.details = dict()
        # Replicas don't have any details of their own; can't run clear here
        # because instance and replica both point to the same details dictionary
        # at first. 
                                      
        # Replica should have the same local value right now
        if replica._local_value != self._local_value:
            raise IOPMechanicalError

        self.add_line(replica, position=0) #<------------------------------------------------------------------------------------or whatever the lowest is?

        # Start with a generally shallow copy that picks up all of the tags.
        # Goal is to preserve tags like "hardcoded" or "do not touch". If
        # enforce_rules is True, "do not touch" would not transfer to the
        # replica because the copy counts as an "out" move. Then, if the
        # original value was to somehow get reset to None, the lineitem could
        # get behind and the entire financials unit could lose a special processing trigger.

    def _sum_details(self, ordered=False):
        """


        Line._sum_details() -> None or number


        Return sum of all details or None if all of the details have a None
        value. Method distinguishes between 0s and None.
        """
        result = None
        #if ordered, can go through get_ordered()
        for detail in self.details.values():
            if detail.value is None:
                continue
            else:
                result = result or 0
                result += detail.value
        return result
