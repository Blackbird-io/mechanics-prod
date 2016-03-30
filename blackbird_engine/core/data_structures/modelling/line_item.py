#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.line_item
"""

Module defines a class of Statemenets with value.  
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LineItem              a Statement that has its own value
====================  ==========================================================
"""




# Imports
import copy
import time

import bb_settings
import bb_exceptions
import tools.for_printing as printing_tools

from data_structures.guidance.guide import Guide
from data_structures.system.tags import Tags
from data_structures.serializers.chef import data_management as xl_mgmt

from .equalities import Equalities
from ._new_statement import Statement




# Constants
T_CONSOLIDATED = Tags.tagManager.catalog["consolidated"]
T_REPLICA = Tags.tagManager.catalog["ddr"]

# Classes
class LineItem(Statement):
    """

    A LineItem is a Statement that can have a value and a position.

    A LineItem can have value in two ways. First, an instance can define
    local value. A local value is written directly to that instance via
    set_value() at some point. The instance log tracks any changes to local
    value.

    Second, a Line can have value because it contains details that have value.
    In such an event, the line's value is always the sum of its parts.

    When you add details to a line that already has a local value, the instance
    will automatically move its local value to a replica detail. After the
    operation, the instance value will be the sum of its old local value, now
    stored in the replica detail, and the other details.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    guide                 instance of Guide object
    log                   list of entries that modified local value
    value                 instance value
    xl                    instance of LineData record set
    
    FUNCTIONS:
    clear()               if modification permitted, sets value to None
    copy()                returns a new line w copies of key attributes
    set_value()           sets value to input, records signature
    ====================  ======================================================
    """
    keyAttributes = Statement.keyAttributes + ["value", "requiredTags", "optionalTags"]

    # Make sure that equality analysis skips potentially circular pointers like
    # .parentObject. Otherwise, comparing children could look to parent, which could
    # look to child, and so on. 
    
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
        # We intentionally use inheritance for the Statement relationship here
        # because then the .find_ and .add_ methods map right on top of each
        # other by default. 

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

        self.xl = xl_mgmt.LineData()

    # Lines can contain a mutable set of details, so we don't include a hash
    # method. Since it's difficult to compare lines to each other unless you
    # know exactly what the user has in mind, we don't support set operations
    # out of the box. Otherwise, you might get a response that a line is "in"
    # a particular set that actually contains an instance with the
    # same value but very different details. 
                                  
    @property
    def value(self):
        """
        read-only property
        """
        result = self._local_value
        # Could be None

        if self._details:
            result = self._sum_details()

        return result

    def __str__(self):
        result = "\n".join(self._get_line_strings())
        result += "\n"
        return result

    def clear(self, recur=True, force=False):
        """


        Line.clear() -> None


        Clear value from instance and optionally details (if ``recur`` is True).
        If instance fails Tags.checkTouch(), will throw exception unless
        ``force`` is True. 
        """
        if self.checkTouch() or force:
            if self._details:
                self._bring_down_local_value()
                if recur:
                    Statement.reset(self)

            sig = self.SIGNATURE_FOR_VALUE_RESET
            self.set_value(None, sig, override=True)

            self.xl = xl_mgmt.LineData()
            # Start with a clean slate for Excel tracking
            
        else:
            comment = "Unable to clear value from line."
            raise bb_exceptions.BBAnalyticalError(c, self)
            
    def copy(self, enforce_rules=True):
        """


        Line.copy() -> Line


        Return a deep copy of the instance and its details. If enforce_rules is
        True, copy conforms to ``out`` rules.
        """
        new_line = Statement.copy(self, enforce_rules)
        # Shallow copy, should pick up _local_value as is, and then create
        # independent containers for tags. 
        
        new_line.guide = copy.deepcopy(self.guide)
        new_line.log = self.log[:]
        
        new_line.xl = xl_mgmt.LineData()

        return new_line

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

        # We include this feature only to show that delegation takes place
        # explicitly. Real work runs through .copy() for default process
        # and through statement logic for the more complex versions. A Line
        # only differs from Statement by its log and local value, and .copy()
        # picks up both.
      
    def increment(self, matching_line, signature=None, consolidating=False):
        """


        Line.increment() -> None


        Increment line value by matching line and details. If ``consolidating``
        is True, method will tag lines accordingly when incrementing local
        value. 
        """
        if matching_line.value is None:
            pass

        else:
            if matching_line._details:
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

                    self.xl.consolidated.sources.append(matching_line)

    # Upgrade-F: The new line structure gives us the option to implement a
    # different approach to line calculation. Basically, we can allow drivers to
    # write "on top" of consolidated lines. So a parent unit can consolidate
    # results from children and then add its own to the same line with the same
    # driver (e.g., rent). The driver would have to increment the line instead
    # of writing a clean value, but that's a simple driver-level change.
    #
    # One existing alternative is to capture the parallel "operating" activities
    # of parent in a separate child unit that kind of resembles our line replica.
    # Consolidating the parent would then combine results from the real children
    # and the replica.
    #
    # A benefit to the "incremental driver" approach is that we can make
    # driver calculations depend on the profile (count, type, etc.) of the
    # parent's children.
    #
    # But you can also do the same thing by adding unique lines to the parent
    # that won't overlap with those of the children and running the computation
    # there.

    def setValue(self, value, signature,
                 overrideValueManagement=False):
        """

        **OBSOLETE**

        Legacy interface for set_value()


        L.setValue() -> None


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
            
        new_value = value
        if new_value is None:
            self._local_value = new_value

        else:
            if self._details:
                m = "Cannot assign new value to a line with existing details."
                raise PermissionError(m)
            else:
                self._local_value = value

        log_entry = (signature, time.time(), value)
        self.log.append(log_entry)
            
            
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
                
                starting_value = replica.value or 0
                new_value = starting_value + self._local_value
                # We know that instance has a non-None value, otherwise we
                # would be in the no-op block.
                replica.set_value(new_value, sig)
                replica.inheritTagsFrom(self)

            else:
                self._make_replica()
                # New replica will come with existing local value

            self.set_value(None, sig, override=True)

    def _get_line_strings(self, indent=TAB_WIDTH):
        """


        LineItem._get_line_strings() -> list


        Return list of one or more strings that describe this line and any
        details. Lines have raw ends. 
        """

        result = []
        
        if not self._details:
            # Simple view: only the local value
            simple = printing_tools.format_as_line(self, left_tab=indent)
            result.append(simple)
        else:
            # Detailed view: when this line has details
            self._bring_down_local_value()
            
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


        LineItem._get_replica() -> LineItem or None


        Get existing replica from details, return result (None if no replica). 
        """
        replica = self._details.get(self.name)
        return replica

    def _make_replica(self):
        """


        LineItem._make_replica() -> LineItem


        Create a replica, add replica to details, return the replica. 
        """
        replica = Tags.copy(self, enforce_rules=False)
        # Start with a shallow copy that picks up all the tags, including ones
        # like "hardcoded" or "do not touch" that don't normally go ``out``. If
        # enforce_rules is True, these would not transfer to the replica because
        # the copy counts as an "out" move. Then, if the original value was to
        # somehow get reset to None, the lineitem could get behind and the
        # entire financials unit could lose a special processing trigger.
        
        replica._details = dict()
        # Replicas don't have any details of their own. Can't run .clear() here
        # because instance and replica initially point to the same details dict.
        replica.tag(T_REPLICA)
                                      
        if replica._local_value != self._local_value:
            comment = "At creation, replica should have the same value as instance."
            raise bb_exceptions.IOPMechanicalError(c)

        self.add_line(replica, position=0)
        # Add replica in first position.

        return replica

    def _sum_details(self):
        """


        Line._sum_details() -> None or number


        Return sum of all details or None if all of the details have a None
        value. Method distinguishes between 0s and None.
        """
        if bb_settings.DEBUG_MODE:
            pool = sorted(self._details.values(),
                          key=lambda line: line.position)
        else:
            pool = self._details.values()

        result = None
        for detail in pool:
            if detail.value is None:
                continue
            else:
                result = result or 0
                result += detail.value
        return result
