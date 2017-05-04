# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.line_item
"""

Module defines a class of BaseFinancialComponent with value.
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
from data_structures.system.tags import Tags

from .base_financial_component import BaseFinancialsComponent
from .history_line import HistoryLine
from .line_item_usage import LineItemUsage




# Constants
SPECIAL_CONSOLIDATION_LINE_PREFIX = ""
SPECIAL_CONSOLIDATION_LINE_SUFFIX = " (consolidated)"
SUMMARY_TYPES = ('skip', 'derive', 'sum', 'average', 'ending', 'starting')


# Classes
class LineItem(BaseFinancialsComponent, HistoryLine):
    """

    A LineItem is a BaseFinancialsComponent that can have a value and a
    position.

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
    id                    instance of ID object, holds unique BBID for instance
    hardcoded             bool; if True, set_value() or clear() will not operate
    include_details       bool; whether or not to consolidate details to parent
    log                   list of entries that modified local value
    position              int; instance's relative position in a Statement
    replica               bool; whether line item is replica
    sum_details           bool; whether line gets its value from summing details
    sum_over_time         bool; whether the line item should be balanced or summed
    summary_count         int; how many periods contributed to line's value
    summary_type          str; how to summarize line's value over time
    value                 instance value
    workspace             dict; unstructured data hoard
    xl                    instance of LineData record set

    FUNCTIONS:
    assign_driver()       assigns driver ID to the line for derivation
    clear()               if modification permitted, sets value to None
    copy()                returns a new line w copies of key attributes
    get_driver()          return Driver assigned to the line
    has_own_content()     checks if line has content
    increment()           add data from another line
    increment_value()     add value from another line
    link_to()             links lines in Excel
    peer_locator()        returns a function for locating or creating a copy of
                          the instance within a given container
    portal_locator()      returns a dict with info needed to locate this line
                          within a model without object references.
    register()            registers instance in namespace and assigns ID
    remove_driver()       removes driver assignment
    set_consolidate()     sets private attribute _consolidate
    set_hardcoded()       sets private attribute _hardcoded
    set_name()            custom method for setting instance name, updates ID
    set_value()           sets value to input, records signature
    to_database()           creates a flattened version of LineItem for Portal

    CLASS METHODS:
    from_database()         class method, extracts LineItem out of API-format
    ====================  ======================================================
    """
    keyAttributes = BaseFinancialsComponent.keyAttributes + ["value",
                                                             "tags.required",
                                                             "tags.optional"]

    # Make sure that equality analysis skips potentially circular pointers like
    # .relationships.parent. Otherwise, comparing children could look to
    # parent, which could look to child, and so on.

    SIGNATURE_FOR_COPY = "LineItem.copy"
    SIGNATURE_FOR_CREATION = "__init__"
    SIGNATURE_FOR_VALUE_RESET = "LineItem.resetValue"
    SIGNATURE_FOR_REPLICA_MANAGEMENT = "Bringing down value."
    SIGNATURE_FOR_INCREMENTATION = "Incremented "
    SIGNATURE_FOR_LINKING_STATEMENTS = "LineItem.link_to"

    SUMMARY_PREFIX = ""  # "total "

    TAB_WIDTH = 3

    def __init__(self, name=None, value=None, parent=None, period=None):
        BaseFinancialsComponent.__init__(self,
                                         name=name,
                                         parent=parent,
                                         period=period)

        self._local_value = None

        self.guide = Guide(priority=3, quality=1)
        self.log = []
        self.position = None

        # summary_type determines how the line is summarized
        self.summary_type = 'sum'

        # summary_count is used for summary_type == 'average'
        self.summary_count = 0

        self._consolidate = True
        self._replica = False
        self._hardcoded = False
        self._include_details = True
        self._sum_details = True
        self.id = ID()
        self._driver_id = None

        if value is not None:
            self.set_value(value, self.SIGNATURE_FOR_CREATION)

        self.workspace = dict()
        self.usage = LineItemUsage()
        self.xl = xl_mgmt.LineData(self)

    def __str__(self):
        result = "\n".join(self._get_line_strings())
        result += "\n"
        return result

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
    def include_details(self):
        return self._include_details

    @include_details.setter
    def include_details(self, val):
        if isinstance(val, bool):
            self._include_details = val
        else:
            msg = "lineitem._include_details can only be set to a boolean value"
            raise(TypeError(msg))

    @property
    def replica(self):
        """
        read-only property
        """
        return self._replica

    @property
    def sum_details(self):
        return self._sum_details

    @sum_details.setter
    def sum_details(self, val):
        if isinstance(val, bool):
            self._sum_details = val
        else:
            msg = "LineItem.sum_details can only be set to a boolean value"
            raise(TypeError(msg))

    @property
    def sum_over_time(self):
        """
        Default value of sum_over_time is True.  If False, line.value will not
        be summed over time and only the end point will be shown in summaries.
        If True, line item will be summed over time for summaries.
        """
        return self.summary_type == 'sum'

    @sum_over_time.setter
    def sum_over_time(self, value):
        self.summary_type = 'sum' if value else None

    @property
    def value(self):
        """
        read-only property
        """
        result = self._local_value
        # Could be None

        if self._details and self.sum_details:
            result = self._get_sum_of_details()

        return result

    @classmethod
    def from_database(cls, data, statement):
        """


        LineItem.from_database() -> None

        **CLASS METHOD**

        Method deserializes all LineItems belonging to ``statement``.
        """
        # first pass: create a dict of lines

        new = cls(
            parent=None,
        )
        new.tags = Tags.from_database(data['tags'])

        id_str = data['driver_id']
        if id_str:
            new._driver_id = ID.from_database(id_str).bbid

        # defer resolution of .xl
        new.xl = xl_mgmt.LineData(new)
        new.xl.format = xl_mgmt.LineFormat.from_database(data['xl_format'])

        new.summary_type = data['summary_type']
        new.summary_count = data['summary_count']
        new._consolidate = data['consolidate']
        new._replica = data['replica']
        new._include_details = data['include_details']
        new._sum_details = data['sum_details']
        new.log = data['log']

        new.guide = Guide.from_database(data['guide'])
        new.id.bbid = ID.from_database(data['bbid']).bbid

        position = data['position']
        position = int(position) if position else None
        new.position = position

        workspace = data.get('workspace', None)
        if workspace:
            new.workspace.update(workspace)

        usage = data.get('usage', None)
        if usage:
            new.usage = LineItemUsage.from_database(usage)

        return new

    def to_database(self, top_level=False):
        """


        LineItem.to_database() -> dict

        Method returns a serialized representation of a LineItem.
        """
        parent_bbid = None
        if not top_level:
            parent_line = self.relationships.parent
            parent_bbid = parent_line.id.bbid.hex if parent_line else None

        result = BaseFinancialsComponent.to_database(self)

        row = {
            'parent_bbid': parent_bbid,
            'position': self.position,
            'summary_type': self.summary_type,
            'summary_count': self.summary_count,
            'consolidate': self._consolidate,
            'replica': self._replica,
            'include_details': self._include_details,
            'sum_details': self._sum_details,
            'xl_format': self.xl.format.to_database(),
            'log': self.log,
            'driver_id': self._driver_id.hex if self._driver_id else None,
            'link': False,
            'guide': self.guide.to_database(),
            'workspace': self.workspace,
            'usage': self.usage.to_database(),
        }

        result.update(row)

        return result

    def assign_driver(self, driver_id):
        """


        LineItem.assign_driver() -> None

        --``driver_id`` is the UUID associated with the driver that should run
        on the line

        Method assigns the given driver_id to the Line.
        """
        self._driver_id = driver_id

    def clear(self, recur=True, force=False, keep_format=True):
        """


        Line.clear() -> None


        Clear value from instance and optionally details (if ``recur`` is True).
        No-op if line is hardcoded, unless ``force`` is True.
        """
        if self.hardcoded and not force:
            pass
        else:
            consolidate = self.consolidate
            if self._details:
                self._bring_down_local_value()
                if recur:
                    BaseFinancialsComponent.reset(self)

            sig = self.SIGNATURE_FOR_VALUE_RESET
            self.set_value(None, sig, override=True)

            format2keep = self.xl.format.copy()
            self.xl = xl_mgmt.LineData(self)

            if keep_format:
                self.xl.format = format2keep

            self._update_stored_xl()

            self.set_consolidate(consolidate)
            # Start with a clean slate for Excel tracking, except for
            # number format

            self.summary_count = 0

    def copy(self, check_include_details=False, clean=False):
        """


        Line.copy() -> Line


        Return a deep copy of the instance and its details. If  is
        True, copy conforms to ``out`` rules.
        """
        new_line = BaseFinancialsComponent.copy(self,
                                  check_include_details=check_include_details,
                                  clean=clean)
        # Shallow copy, should pick up _local_value as is, and then create
        # independent containers for tags.

        new_line.guide = copy.deepcopy(self.guide)
        new_line.log = self.log[:]
        new_line._sum_over_time = self.sum_over_time
        new_line._include_details = self.include_details
        new_line._sum_details = self.sum_details
        new_line._driver_id = copy.copy(self._driver_id)
        new_line.set_consolidate(self._consolidate)
        new_line.id = copy.copy(self.id)
        new_line.usage = self.usage.copy()
        new_line.workspace = self.workspace.copy()
        new_line.xl = xl_mgmt.LineData(new_line)
        new_line.xl.format = self.xl.format.copy()

        if not clean:
            new_line.set_hardcoded(self._hardcoded)
            if check_include_details and not new_line._details and self._details:
                new_line.set_value(self.value, self.SIGNATURE_FOR_COPY,
                                   override=True)
        else:
            new_line._hardcoded = False
            new_line._local_value = None
            new_line.log = []

        return new_line

    def get_driver(self):
        """


        LineItem.get_driver() -> Driver or None

        Method returns Driver object that is assigned to the instance or None.
        """
        dr = None
        if self._driver_id:
            parent = self.relationships.parent
            while isinstance(parent, BaseFinancialsComponent):
                parent = parent.relationships.parent

            bu = parent.relationships.parent
            mo = bu.relationships.model
            dr = mo.drivers.get(self._driver_id)

        return dr

    def has_own_content(self):
        """


        LineItem.has_own_content() -> Bool

        Checks if line has content. A line with own content should have no
        children with own content, and should not consolidate
        """
        return any((
            len(self._details) > 0,
            self.xl.derived.calculations,
            self.hardcoded,
        ))

    def increment(self, matching_line, signature=None, consolidating=False,
                  xl_label=None, override=False, xl_only=False,
                  over_time=False):
        """


        Line.increment() -> None


        Increment line value by matching line and details. If ``consolidating``
        is True, method will tag lines accordingly when incrementing local
        value.
        """
        send_to_statement = matching_line._details and \
                            (matching_line.include_details or over_time)
        if send_to_statement:
            BaseFinancialsComponent.increment(self, matching_line,
                                              consolidating=consolidating,
                                              xl_label=xl_label,
                                              over_time=over_time,
                                              override=override,
                                              xl_only=xl_only)
            # Use Statement method here because we're treating the matching
            # line as a Statement too. We assume that its details represent
            # all of its value data. Statement.increment() will copy those
            # details to this instance.
        elif matching_line.value is None:
            if self.consolidate and consolidating:
                self.xl.add_consolidated_source(matching_line, label=xl_label)
        else:
            if signature is None:
                signature = self.SIGNATURE_FOR_INCREMENTATION

            allowed = (consolidating and (self.consolidate or override)) \
                      or not consolidating

            if allowed:
                if self._details:
                    # 1) determine the name for the consolidation line
                    con_line_name = SPECIAL_CONSOLIDATION_LINE_PREFIX
                    con_line_name += matching_line.name
                    con_line_name += SPECIAL_CONSOLIDATION_LINE_SUFFIX

                    # 2) look in details for the consolidation line
                    # if line does NOT exist, make it
                    if con_line_name not in self._details:
                        new_line = LineItem(name=con_line_name)

                        if self._restricted:
                            c = "Trying to add line to restricted parent line"
                            raise ValueError(c)

                        if not over_time:
                            new_line.remove_driver()
                        self.append(new_line)

                    # 3) increment line with the matching_line
                    own_line = self._details[con_line_name]
                    own_line.increment(matching_line,
                                       consolidating=consolidating,
                                       xl_only=xl_only,
                                       override=override)
                else:
                    new_value = self.increment_value(matching_line)

                    if not xl_only:
                        self.set_value(new_value, signature)

                    if consolidating:
                        if not xl_only:
                            self.tags.inherit_from(matching_line.tags)
                            self._consolidated = True

                        self.xl.add_consolidated_source(matching_line,
                                                        label=xl_label)

    def increment_value(self, matching_line):
        """


        LineItem.increment_value() -> float

        --``matching_line`` is another LineItem

        Add matching_line's value to self in a manner consistent with out
        summary_type.
        """

        old_value = self.value or 0
        if self.summary_type == 'average':
            new_value = (
                old_value * self.summary_count + matching_line.value
                ) / (self.summary_count + 1)
            self.summary_count += 1
        else:
            new_value = old_value + matching_line.value
        return new_value

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
            # this part should only live in LineItem since statements don't
            # have xl data
            self.set_value(matching_line.value,
                           signature=self.SIGNATURE_FOR_LINKING_STATEMENTS,
                           override=True)
            self.xl.set_ref_source(matching_line)

    def peer_locator(self):
        """


        LineItem.peer_locator() -> LineItem

        Given a parent container from another time period, return a function
        locating a copy of ourselves within that container.
        """

        def locator(statement, create=True, **kargs):
            peer = statement.find_first(self.name)
            if create and not peer:
                peer = self.copy()
                peer.clear()
                statement.add_line(peer)
            return peer

        return locator

    def portal_locator(self):
        """


        LineItem.portal_locator() -> dict

        Method returns a dict with info needed to locate this line within
        a model without object references.
        """
        parent = self.relationships.parent
        while isinstance(parent, BaseFinancialsComponent):
            statement = parent
            parent = parent.relationships.parent

        # parent is Financials at this point
        financials = parent

        statement_attr = None
        for attr in financials._full_order:
            stmt = getattr(financials, attr, None)
            if stmt is statement:
                statement_attr = attr

        bu = financials.relationships.parent
        locator = dict(
            buid=bu.id.bbid.hex,
            financials_attr=statement_attr,
            bbid=self.id.bbid.hex,
        )

        period = financials.period
        if period:
            period_end = format(period.end)
            time_line = period.relationships.parent
        else:
            period_end = None
            time_line = bu.relationships.model.time_line

        locator.update(
            period=period_end,
            resolution=time_line.resolution,
            name=time_line.name,
        )

        return locator

    def remove_driver(self, recur=False):
        """


        LineItem.remove_driver() -> None

        Method removes driver ID assignment.
        """
        self._driver_id = None
        if recur:
            for line in self._details.values():
                line.remove_driver(recur=recur)

    def register(self, namespace):
        """


        LineItem.register() -> None

        --``namespace`` is the namespace to assign to instance

        Method sets namespace of instance and assigns BBID.  Method recursively
        registers components.
        """
        BaseFinancialsComponent.register(self, namespace)

        self._update_stored_hc()
        self._update_stored_value()

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

    def set_hardcoded(self, val, recur=False):
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

        self._update_stored_hc()

        if recur:
            for line in self._details.values():
                line.set_hardcoded(val, recur=recur)

    def set_name(self, name):
        """


        LineItem.set_name() -> None

        --``name`` is the string name to assign to the LineItem

        Method sets the name on the LineItem and updates its ID to reflect the
         name change.  Line's details also get their IDs updated.

        Delegates to base-class method.
        """
        # SHOULD REMOVE OLD VALUES FROM PERIOD DATA CACHE!!!!
        BaseFinancialsComponent.set_name(self, name)
        self.register(self.id.namespace)

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
            try:
                test = value + 1
            except TypeError:
                print(self)
                c = "Cannot perform arithmetic on LineItem! override=False"
                raise bb_exceptions.BBAnalyticalError(c)
                # Will throw exception if value doesn't support arithmetic

            if self.hardcoded:
                return  # Do  Nothing if line is hardcoded

        new_value = value
        if new_value is None:
            self._local_value = new_value
        else:
            if self._details and self.sum_details:
                print(self)
                m = "Cannot assign new value to a line with existing details."
                raise bb_exceptions.BBPermissionError(m)
            else:
                self._local_value = value

        log_entry = (signature, time.time(), value)
        self.log.append(log_entry)
        self._update_stored_value()

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _bind_and_record(self, line, noclear=False):
        """


        Statement._bind_and_record() -> None


        Set instance as line parent, add line to details.
        """

        # We need to deal with the case where a line already has an assigned
        # value, but is now being assigned a detail line.  We will add the
        # existing value as an additional detail line with the currently
        # assigned value
        if self._local_value and not self._details and self.sum_details:
            self._bring_down_local_value()

        BaseFinancialsComponent._bind_and_record(self, line, noclear=noclear)

        self._update_stored_hc()
        line._update_stored_value()

    def _bring_down_local_value(self):
        """


        Line._bring_down_local_value() -> None


        Bring down instance's local value to replica. No-op if local value is
        None.
        """
        if self._local_value is None or not self.sum_details:
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

            footer = printing_tools.format_as_line(self,
                                                   prefix=self.SUMMARY_PREFIX,
                                                   left_tab=indent)
            result.append(footer)

        return result

    def _get_sum_of_details(self):
        """


        Line._get_sum_of_details() -> None or number


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

    def _make_replica(self):
        """


        LineItem._make_replica() -> None


        Create a replica, add replica to details
        """
        replica = copy.copy(self)
        replica.tags = self.tags.copy()
        replica._details = dict()
        replica.xl = xl_mgmt.LineData(replica)
        replica.xl.format = self.xl.format.copy()
        replica.set_consolidate(self._consolidate)
        replica._period = self.period
        replica._replica = True
        replica.position = 0
        replica.register(namespace=self.id.namespace)

        self._details[replica.tags.name] = replica

    def _update_stored_value(self, recur=True):
        """
        Method updates cached value in the Period's value directory so that it
         will be preserved in the database.
        """
        if self.period:
            self.period.update_line_value(self)

        if recur:
            parent = self.relationships.parent
            if isinstance(parent, LineItem):
                parent._update_stored_value()

    def _update_stored_xl(self):
        """
        Method updates cached Excel data in the Period's value directory
        so that it will be preserved in the database.
        """
        if self.period:
            self.period.update_line_xl(self)

    def _update_stored_hc(self):
        """
        Method updates cached hardcoded value in the Period's value directory
        so that it will be preserved in the database.
        """
        if self.period:
            self.period.update_line_hardcoded(self)

        for line in self._details.values():
            line._update_stored_hc()
