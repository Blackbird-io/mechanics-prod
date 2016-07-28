# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.statement
"""

Module defines Statement, a container for lines.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Statement             container that stores, updates, and organizes LineItems
====================  ==========================================================
"""




# Imports
import copy

import bb_exceptions
import bb_settings

from data_structures.system.relationships import Relationships
from data_structures.system.tags import Tags
from data_structures.system.tags_mixin import TagsMixIn
from data_structures.system.bbid import ID

from .equalities import Equalities




# Constants
# n/a

# Globals
# n/a

# Classes
class Statement(Equalities, TagsMixIn):
    """

    A Statement is a container that supports fast lookup and ordered views.

    CONTAINER:

    Statements generally contain Lines, which may themselves contain additional
    Lines. You can use Statement.find_first() or find_all() to locate the
    item you need from the top level of any statement.

    You can add details to a statement through add_line(). Statements also
    support the append() and extend() list interfaces.

    You can easily combine statements by running stmt_a.increment(stmt_b).

    ORDER:

    Statements provide ordered views of their contents on demand through
    get_ordered(). The ordered view is a list of details sorted by their
    relative position.

    Positions should be integers GTE 0. Positions can (and usually should) be
    non-consecutive. You can specify your own positions when adding a detail or
    have the Statement automatically assign a position to the detail. You can
    change detail order by adjusting the .position attribute of any detail.

    Statement automatically maintains and repairs order. If you add a line in
    an existing position, the Statement will move the existing lines and all
    those behind it back. If you manually change the position of one line to
    conflict with another, Statement will sort them in alphabetical order.

    RECURSION:

    You can view the full, recursive list of all the details in a statement
    by running stmt.get_full_ordered().

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    consolidated          whether Statement has been consolidated
    POSITION_SPACING      default distance between positions
    relationships         instance of Relationships class

    FUNCTIONS:
    add_line()            add line to instance
    append()              add line to instance in final position
    copy()                return deep copy
    extend()              append multiple lines to instance in order
    find_all()            return all matching items
    find_first()          return the first matching item
    get_ordered()         return list of instance details
    get_full_ordered()    return recursive list of details
    increment()           add data from another statement
    link_to()             links statements in Excel
    reset()               clear values
    ====================  ======================================================
    """
    keyAttributes = ["_details"]
    # Should rename this comparable_attributes

    def __init__(self, name=None, spacing=100):
        TagsMixIn.__init__(self, name)

        self._consolidated = False
        self._details = dict()
        self.relationships = Relationships(self)

        if spacing < 1:
            raise error
        if not isinstance(spacing, int):
            raise error

        self.POSITION_SPACING = spacing
        self.id = ID() # does not get its own bbid, just holds namespace

    def __eq__(self, comparator, trace=False, tab_width=4):
        """


        Statement.__eq__() -> bool


        Method explicitly delegates work to Equalities.__eq__(). The Financials
        class defines keyAttributes as an empty list at the class level, so
        Equalities will run pure-play list.__eq__() comparison logic, but still
        support tracing.
        """
        return Equalities.__eq__(self, comparator, trace, tab_width)

    def __ne__(self, comparator, trace=False, tab_width=4):
        """


        Statement.__ne__() -> bool


        Method explicitly delegates all work to Equalities.
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)

    def __str__(self):
        result = "\n"

        header = str(self.tags.name).upper()
        header = header.center(bb_settings.SCREEN_WIDTH)
        result += header
        result += "\n\n"

        if self._details:
            for line in self.get_ordered():
                result += str(line)
        else:
            comment = "[intentionally left blank]"
            comment = comment.center(bb_settings.SCREEN_WIDTH)
            comment = "\n" + comment

            result += comment

        result += "\n\n"

        return result

    @property
    def has_been_consolidated(self):
        """
        read-only property.
        """
        return self._consolidated

    def add_line(self, new_line, position=None):
        """


        Statement.add_line() -> None


        Add line to instance at position.

        If ``position`` is None, method appends line. If position conflicts
        with existing line, method will place it at the requested position
        and push back all of the lines behind it by POSITION_SPACING.
        """
        self._inspect_line_for_insertion(new_line)

        if position is None:
            self.append(new_line)

        else:
            new_line.position = position

            if not self._details:
                self._bind_and_record(new_line)
                # This block differs from append in that we preserve the
                # requested line position

            else:
                ordered = self.get_ordered()

                if new_line.position < ordered[0].position or ordered[-1].position < new_line.position:

                    self._bind_and_record(new_line)
                    # Requested position falls outside existing range. No
                    # conflict, insert line as is.

                else:

                    # Potential conflict in positions. Spot existing, adjust as
                    # necessary.
                    for i in range(len(ordered)):
                        existing_line = ordered[i]

                        if new_line.position < existing_line.position:
                            self._bind_and_record(new_line)
                            break
                            # If we get here, ok to insert as-is. New position
                            # could only conflict with lines below the current
                            # because we are going through the lines in order.
                            # But we know that the line does not because the
                            # conflict block breaks the loop.

                        elif new_line.position == existing_line.position:
                            # Conflict resolution block.

                            tail = ordered[i:]
                            for pushed_line in tail:
                                pushed_line.position += self.POSITION_SPACING

                            self._bind_and_record(new_line)
                            break

                        else:
                            continue

    def add_line_to(self, line, *ancestor_tree):
        """

        **OBSOLETE**

        Legacy interface for find_first() and add_line().


        Statement.add_line_to() -> None


        Method adds line to instance. ``ancestor_tree`` is a list of 1+ strings.
        The strings represent names of lines in instance, from senior to junior.
        Method adds line as a part of the most junior member of the ancestor
        tree.

        Method will throw KeyError if instance does not contain the ancestor tree
        in full.

        EXAMPLE:

        >>> F = Statement()
        >>> ...
        >>> print(F)

        revenue ............................None
          mens  ............................None
            footwear .......................None

        >>> sandals = LineItem("sandals")
        >>> sandals.setValue(6, "example")
        >>> F.add_line_to(sandals, "revenue", "mens", "footwear")
        >>> print(F)

        revenue ............................None
          mens  ............................None
            footwear .......................None
              sandals..........................6
        """
        if ancestor_tree:
            detail = self.find_first(*ancestor_tree)
            if detail is None:
                raise KeyError(ancestor_tree)
            else:
                detail.add_line(line)
        else:
            self.append(line)

    def add_top_line(self, line, after=None):
        """

        **OBSOLETE**

        Legacy interface for add_line()


        Statement.add_top_line() -> None


        Insert line at the top level of instance. Method expects ``after`` to
        be the name of the item after which caller wants to insert line. If
        ``after`` == None, method appends line to self.
        """
        if after:
            new_position = self._details[after].position + self.POSITION_SPACING
            self.add_line(line, new_position)
        else:
            self.append(line)

    def append(self, line):
        """


        Statement.append() -> None


        Add line to instance in final position.
        """
        self._inspect_line_for_insertion(line)
        # Will throw exception if problem

        ordered = self.get_ordered()
        if ordered:
            last_position = ordered[-1].position
        else:
            last_position = 0
        new_position = last_position + self.POSITION_SPACING
        line.position = new_position

        self._bind_and_record(line)

    def copy(self):
        """


        Statement.copy() -> Statement


        Method returns a deep copy of the instance and any details. If
        ```` is True, copy will conform to ``out`` rules.
        """
        result = copy.copy(self)
        result._consolidated = False
        result.tags = self.tags.copy()
        result.relationships = self.relationships.copy()

        # Tags.copy returns a shallow copy of the instance w deep copies
        # of the instance tag attributes.
        result._details = dict()
        # Clean dictionary

        if bb_settings.DEBUG_MODE:
            pool = self.get_ordered()
        else:
            pool = self._details.values()

        for own_line in pool:
            new_line = own_line.copy()
            result.add_line(new_line, position=own_line.position)
            # Preserve relative order

        return result

    def extend(self, lines):
        """


        Statement.extend() -> None


        lines can be either an ordered container or a Statement object
        """
        try:
            for line in lines:
                self.append(line)
        except TypeError:
            for line in lines.get_ordered():
                self.append(line)

    def find_all(self, *ancestor_tree, remove=False):
        """


        Statement.find_all() -> list


        Return a list of details that matches the ancestor_tree.

        The ancestor tree should be one or more strings naming objects in order
        of their relationship, from most junior to most senior.

        Method searches breadth-first within instance, then depth-first within
        instance details.

        If ``remove`` is True, method **removes** the result from its parent
        prior to delivery.

        NOTE: Use caution when removing items through this method, since you may
        have difficulty putting them back.

        For most removal tasks, find_first(remove=True) will offer significantly
        more comfort at a relatively small performance cost.
        """
        result = []

        caseless_root_name = ancestor_tree[0].casefold()
        if remove:
            root = self._details.pop(caseless_root_name, None)
            # Pull root out of details
        else:
            root = self._details.get(caseless_root_name)
            # Keep root in details

        if root:
            remainder = ancestor_tree[1:]
            if remainder:
                lower_nodes = root.find_all(*remainder, remove=remove)
                if lower_nodes:
                    result.extend(lower_nodes)
            else:
                # Nothing left, at the final node
                node = root
                result.append(node)
        else:
            for detail in self.get_ordered():
                lower_nodes = detail.find_all(*ancestor_tree, remove=remove)
                if lower_nodes:
                    result.extend(lower_nodes)
                    continue

        return result

    def find_first(self, *ancestor_tree, remove=False):
        """


        Statement.find_first() -> Line or None


        Return a detail that matches the ancestor tree or None.

        The ancestor tree should be one or more strings naming objects in order
        of their relationship, from most junior to most senior. So if "bubbles"
        is part of "cost", you can run stmt.find_first("bubbles", "cost").

        If only one object named "bubbles" exists in the instance and any of its
        details, a call to stmt.find_first("bubbles") will return the same
        result.

        Method searches breadth-first within instance, then depth-first within
        instance details.

        If ``remove`` is True, method **removes** the result from its parent
        prior to delivery.

        NOTE: Use caution when removing items through this method, since you may
        have difficulty putting them back.

        The best way to reinsert an item you accidentally removed is to find
        its parent using detail.relationships.parent and insert the item directly back.
        """
        result = None

        caseless_root_name = ancestor_tree[0].casefold()
        if remove:
            root = self._details.pop(caseless_root_name, None)
            # Pull root out of details
        else:
            root = self._details.get(caseless_root_name)
            # Keep root in details

        if root:
            remainder = ancestor_tree[1:]
            if remainder:
                result = root.find_first(*remainder, remove=remove)
            else:
                result = root
                # Caller specified one criteria and we matched it. Stop work.

        else:
            for detail in self.get_ordered():
                result = detail.find_first(*ancestor_tree, remove=remove)
                if result is not None:
                    break
                else:
                    continue

        return result

    def get_full_ordered(self):
        """


        Statement.get_full_ordered() -> list


        Return ordered list of lines and their details. Result will show lines
        in order of relative position depth-first.
        """
        result = list()
        for line in self.get_ordered():
            if getattr(line, '_details', None):
                # this allows Step objects (and others not having details) to
                # be held by statement, co-mingled with LineItems, primarily
                # for the purpose of the path
                result.append(line)
                increment = line.get_full_ordered()
                result.extend(increment)
            else:
                result.append(line)
        return result

    def get_ordered(self):
        """


        Statement.get_ordered() -> list


        Return a list of details in order of relative position.
        """
        result = sorted(self._details.values(), key=lambda line: line.position)
        return result

    def increment(self, matching_statement, consolidating=False, xl_label=None,
                  override=False, xl_only=False):
        """


        Statement.increment() -> None


        Increment matching lines, add new ones to instance. Works recursively.

        If ``consolidating`` is True, method sets obj._consolidated = True.
        """
        if bb_settings.DEBUG_MODE:
            pool = matching_statement._get_ordered_items_debug()
        else:
            pool = matching_statement._details.items()

        for name, external_line in pool:
            # ORDER SHOULD NOT MATTER HERE

            # If we get here, the line has survived screening. We now have two
            # ways to add its information to the instance. Option A, is to
            # increment the value on a matching line. Option B is to copy the
            # line into the instance. We apply Option B only when we can't do
            # Option A.

            own_line = self._details.get(name)

            if own_line:
                # Option A
                own_line.increment(external_line, consolidating=consolidating,
                                   xl_label=xl_label, override=override,
                                   xl_only=xl_only)

            else:
                # Option B
                local_copy = external_line.copy()
                # Dont enforce rules to track old line.replicate() method

                if external_line.consolidate or override:
                    if consolidating:
                        if external_line.value is not None:
                            if not local_copy._consolidated and not xl_only:
                                local_copy._consolidated = True

                            # Pick up lines with None values, but don't tag
                            # them. We want to allow derive to write to these
                            # if necessary.

                            # need to make sure Chef knows to consolidate this
                            # source line (or its details) also

                            self._add_lines_in_chef(local_copy, external_line,
                                                    xl_label=xl_label)

                    self.add_line(local_copy, local_copy.position)
                    # For speed, could potentially add all the lines and then fix
                    # positions once.
                else:
                    pass

    def link_to(self, matching_statement):
        """


        Statement.link_to() -> None

        --``matching_statement`` is another Statement object

        Method links lines from instance to matching_statement in Excel.
        """
        for line in self.get_ordered():
            oline = matching_statement.find_first(line.name)
            line.link_to(oline)

    def register(self, namespace):
        """


        Statement.register() -> None

        --``namespace`` is the namespace to assign to instance

        Method sets namespace of instance and assigns BBID.  Method recursively
        registers components.
        """
        self.id.set_namespace(namespace)
        self.id.assign(self.name)

        for line in self.get_ordered():
            line.register(namespace=self.id.namespace)

    def reset(self):
        """


        Statement.reset() -> None


        Clear all values, preserve line shape.
        """
        #clears values, not shape
        if bb_settings.DEBUG_MODE:
            pool = self.get_ordered()
        else:
            pool = self._details.values()

        for line in pool:
            line.clear(recur=True)

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _add_lines_in_chef(self, local_copy, external_line, xl_label=None):
        """


        Statement._add_lines_in_chef() -> None


        Add lines to consolidated.sources list used by Chef.
        """

        # need to make sure Chef knows to consolidate this
        # source line (and its details) also
        if not external_line._details:
            local_copy.xl.consolidated.sources.append(external_line)
            local_copy.xl.consolidated.labels.append(xl_label)
        else:
            for n, l in local_copy._details.items():
                detail_to_append = external_line._details.get(n)

                self._add_lines_in_chef(l, detail_to_append, xl_label)

    def _bind_and_record(self, line):
        """


        Statement._bind_and_record() -> None


        Set instance as line parent, add line to details.
        """
        line.relationships.set_parent(self)
        line.register(namespace=self.id.namespace)

        self._details[line.tags.name] = line

    def _inspect_line_for_insertion(self, line):
        """


        Statement._inspect_line_for_insertion() -> None


        Will throw exception if Line if you can't insert line into instance.
        """
        if not line.tags.name:
            c = "Cannot add nameless lines."
            raise bb_exceptions.BBAnalyticalError(c)

        if line.tags.name in self._details:
            c = "Implicit overwrites prohibited."
            raise bb_exceptions.BBAnalyticalError(c)

    def _get_ordered_items_debug(self):
        """


        Statement._get_ordered_items_debug() -> list of tuples


        Return a list of _detail dictionary items in order of relative
        position. Items are key-value pairings contained in list of tuples.
        """

        items = self._details.items()

        def item_sorter(item):
            line = item[1]
            return line.position

        result = sorted(items, key=item_sorter)

        return result

    def _repair_order(self, starting=0, recur=False):
        """


        Statement._repair_order() -> list


        Build an ordered list of details, then adjust their positions so
        that get_ordered()[0].position == starting and any two items are
        POSITION_SPACING apart. Sort by name in case of conflict.

        If ``starting`` is 0 and position spacing is 1, positions will match
        item index in self.get_ordered().

        Repeats all the way down on recur.
        """

        # Build table by position
        ordered = list()
        by_position = dict()

        if bb_settings.DEBUG_MODE:
            pool = self.get_ordered()
        else:
            pool = self._details.values()

        for line in pool:
            entry = by_position.setdefault(line.position, list())
            entry.append(line)

        # Now, go through the table and build a list
            #can then just assign order to the list

        for position in sorted(by_position):
            lines = by_position[position]
            lines = sorted(lines, lambda x: x.tags.name)
            ordered.extend(lines)

        # Now can assign positions
        for i in range(len(ordered)):
            line = ordered[i]
            new_position = starting + (i * self.POSITION_SPACING)
            line.position = new_position
            if recur:
                line._repair_order(starting=starting, recur=recur)

        # Changes lines in place.
        return ordered
