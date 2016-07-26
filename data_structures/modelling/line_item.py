# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.line_item
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
from data_structures.serializers.chef import data_management as xl_mgmt
from data_structures.system.bbid import ID

from .statement import Statement




# Constants
# n/a

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
    consolidate           bool; whether or not to consolidate line item
    guide                 instance of Guide object
    hardcoded             bool; if True, set_value() or clear() will not operate
    log                   list of entries that modified local value
    value                 instance value
    sum_over_time         bool; whether the line item should be balanced or summed
    xl                    instance of LineData record set
    
    FUNCTIONS:
    clear()               if modification permitted, sets value to None
    copy()                returns a new line w copies of key attributes
    increment()           add data from another line
    link_to()             links lines in Excel
    set_consolidate()     sets private attribute _consolidate
    set_hardcoded()       sets private attribute _hardcoded
    set_value()           sets value to input, records signature
    ====================  ======================================================
    """
    keyAttributes = Statement.keyAttributes + ["value", "tags.required",
                                               "tags.optional"]

    # Make sure that equality analysis skips potentially circular pointers like
    # .relationships.parent. Otherwise, comparing children could look to parent, which
    # could look to child, and so on.
    
    SIGNATURE_FOR_CREATION = "__init__"
    SIGNATURE_FOR_VALUE_RESET = "LineItem.resetValue"
    SIGNATURE_FOR_REPLICA_MANAGEMENT = "Bringing down value."
    SIGNATURE_FOR_INCREMENTATION = "Incremented "

    SUMMARY_PREFIX = ""  # "total "

    TAB_WIDTH = 3
    
    def __init__(self, name=None, value=None):

        Statement.__init__(self, name)
        # We intentionally use inheritance for the Statement relationship here
        # because then the .find_ and .add_ methods map right on top of each
        # other by default. 

        self._local_value = None
        
        self.guide = Guide(priority=3, quality=1)
        self.log = []
        self.position = None
        self._sum_over_time = True
        self._summary_calculate = False
        self._consolidate = True
        self._replica = False
        self._hardcoded = False
        self.id = ID()

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
    def sum_over_time(self):
        """
        Default value of sum_over_time is True.  If False, line.value will not
        be summed over time and only the end point will be shown in summaries.
        If True, line item will be summed over time for summaries.
        """
        return self._sum_over_time

    @sum_over_time.setter
    def sum_over_time(self, value):
        self._sum_over_time = value

    @property
    def summary_calculate(self):
        """
        Default value of summary_calculate is False.  If False, line will be
        dealt with per the value of "sum_over_time".  If True, line item will
        be calculated with any relevant drivers that are "summary_calculate'.
        """
        return self._summary_calculate

    @summary_calculate.setter
    def summary_calculate(self, value):
        self._summary_calculate = value

    @property
    def consolidate(self):
        """
        read-only property. Default value is True
        If False, line.value will not consolidate up to parent business units.
        """
        return self._consolidate

    @property
    def hardcoded(self):
        """
        read-only property. Default value is False
        If True, set_value() and clear() will have no operation
        """
        return self._hardcoded

    @property
    def replica(self):
        """
        read-only property
        """
        return self._replica

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

    def clear(self, recur=True, force=False, keep_format=True):
        """


        Line.clear() -> None


        Clear value from instance and optionally details (if ``recur`` is True).
        No-op if line is hardcoded, unless ``force`` is True.
        """
        if self.hardcoded and not force:
            pass
        else:
            num_format = self.xl.number_format
            consolidate = self.consolidate
            if self._details:
                self._bring_down_local_value()
                if recur:
                    Statement.reset(self)

            sig = self.SIGNATURE_FOR_VALUE_RESET
            self.set_value(None, sig, override=True)

            keep_format = self.xl.format.copy()
            self.xl = xl_mgmt.LineData()

            if keep_format:
                self.xl.format = keep_format

            self.set_consolidate(consolidate)
            # Start with a clean slate for Excel tracking, except for
            # number format
            
    def copy(self):
        """


        Line.copy() -> Line


        Return a deep copy of the instance and its details. If  is
        True, copy conforms to ``out`` rules.
        """
        new_line = Statement.copy(self)
        # Shallow copy, should pick up _local_value as is, and then create
        # independent containers for tags. 
        
        new_line.guide = copy.deepcopy(self.guide)
        new_line.log = self.log[:]
        new_line._sum_over_time = self.sum_over_time
        new_line.set_consolidate(self._consolidate)
        new_line.set_hardcoded(self._hardcoded)
        new_line.id = copy.copy(self.id)
        new_line.xl = xl_mgmt.LineData()

        try:
            new_line.xl.format = self.xl.format.copy()
        except AttributeError:
            import pdb
            pdb.set_trace()

        return new_line

    def increment(self, matching_line, signature=None, consolidating=False,
                  xl_label=None, override=False):
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
                Statement.increment(self, matching_line,
                                    consolidating=consolidating,
                                    xl_label=xl_label,
                                    override=override)
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
            
                if consolidating and (self._consolidate is True or override):
                    self.tags.inherit_from(matching_line.tags)
                    self._consolidated = True
                    self.xl.consolidated.sources.append(matching_line)
                    self.xl.consolidated.labels.append(xl_label)

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

    def link_to(self, matching_line):
        """


        Statement.link_to() -> None

        --``matching_statement`` is another Statement object

        Method links lines to matching_line in Excel.
        """
        if self._details:
            for line in self._details.values():
                oline = matching_line.find_first(line.name)
                line.link_to(oline)
        else:
            # this part should only live in LineItem since statements don't have xl data
            self.xl.reference.source = matching_line

    def register(self, namespace):
        """


        LineItem.register() -> None

        --``namespace`` is the namespace to assign to instance

        Method sets namespace of instance and assigns BBID.  Method recursively
        registers components.
        """
        self.id.set_namespace(namespace)
        self.id.assign(self.name)

        for line in self.get_ordered():
            line.register(namespace=self.id.namespace)

    def set_consolidate(self, val):
        """


        LineItem.set_consolidate() -> None


        --``val`` must be a boolean (True or False)

        Method for explicitly setting self._consolidate.
        """
        if isinstance(val, bool):
            self._consolidate = val
        else:
            msg = "lineitem._consolidate can only be set to a boolean value"
            raise(TypeError(msg))

    def set_hardcoded(self, val):
        """


        LineItem.set_hardcoded() -> None


        --``val`` must be a boolean (True or False)

        Method for explicitly setting self._hardcoded.
        """
        if val is True:
            self._hardcoded = True
        elif val is False:
            self._hardcoded = False
        else:
            msg = "lineitem._hardcoded can only be set to a boolean value"
            raise(TypeError(msg))

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


        Set line value, add entry to log. Value must be numeric.

        Will throw BBPermissionError if line is hardcoded.

        If ``override`` is True, skip type check for value and hardcoded
        control.
        """
        if not override:
            test = value + 1
            # Will throw exception if value doesn't support arithmetic

            if self.hardcoded:
                c = "Line is hardcoded. Cannot write."
                raise bb_exceptions.BBPermissionError(c, self)
            
        new_value = value
        if new_value is None:
            self._local_value = new_value

        else:
            if self._details:
                m = "Cannot assign new value to a line with existing details."
                raise bb_exceptions.BBPermissionError(m)
            else:
                self._local_value = value

        log_entry = (signature, time.time(), value)
        self.log.append(log_entry)
            
    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _bind_and_record(self, line):
        """


        Statement._bind_and_record() -> None


        Set instance as line parent, add line to details.
        """

        # We need to deal with the case where a line already has an assigned
        # value, but is now being assigned a detail line.  We will add the
        # existing value as an additional detail line with the currently
        # assigned value
        if self._local_value and not self._details:
            self._bring_down_local_value()

        Statement._bind_and_record(self,line)

    def _bring_down_local_value(self):
        """


        Line._bring_down_local_value() -> None


        Bring down instance's local value to replica. No-op if local value is
        None.
        """
        if self._local_value is None:
            pass
        else:
            sig = self.SIGNATURE_FOR_REPLICA_MANAGEMENT
            self._make_replica()
            # New replica will come with existing local value, add replica as
            # detail

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

    def _make_replica(self):
        """


        LineItem._make_replica() -> None


        Create a replica, add replica to details
        """
        replica = copy.copy(self)
        replica.tags = self.tags.copy()
        # Start with a shallow copy that picks up all the tags, including ones
        # like "hardcoded" or "do not touch" that don't normally go ``out``. If
        #  is True, these would not transfer to the replica because
        # the copy counts as an "out" move. Then, if the original value was to
        # somehow get reset to None, the lineitem could get behind and the
        # entire financials unit could lose a special processing trigger.
        
        replica._details = dict()
        replica.xl = xl_mgmt.LineData()
        replica.xl.format = self.xl.format.copy()
        replica.set_consolidate(self._consolidate)

        # Replicas don't have any details of their own. Can't run .clear() here
        # because instance and replica initially point to the same details dict.
        replica._replica = True
        replica.position = 0
        replica.register(namespace=self.id.namespace)

        self._details[replica.tags.name] = replica
        # Add replica in first position.

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
