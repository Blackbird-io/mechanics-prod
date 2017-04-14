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

from data_structures.system.bbid import ID
from data_structures.system.tags import Tags

from .base_financial_component import BaseFinancialsComponent
from .line_item import LineItem
from .link import Link




# Constants
# n/a

# Globals
# n/a

# Classes
class Statement(BaseFinancialsComponent):
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

    def __init__(self, name=None, spacing=100, parent=None, period=None):
        BaseFinancialsComponent.__init__(self, name=name, spacing=spacing,
                                         parent=parent, period=period)

    def copy(self, check_include_details=False, clean=False):
        new_stmt = BaseFinancialsComponent.copy(self,
                                                check_include_details=
                                                check_include_details,
                                                clean=clean)

        return new_stmt

    @classmethod
    def from_portal(cls, portal_data, financials):
        """

        Statement.from_portal(portal_data) -> Statement

        **CLASS METHOD**

        Method extracts a Statement from portal_data.
        """
        new = cls(parent=financials)
        new.tags = Tags.from_portal(portal_data['tags'])

        if portal_data['bbid'] is not None:
            new.id.bbid = ID.from_portal(portal_data['bbid']).bbid

        # deserialize all LineItems
        catalog = dict()
        for row in portal_data['lines']:
            if row.get('link'):
                new_line = Link.from_portal(row, new)
            else:
                new_line = LineItem.from_portal(row, new)

            parent_id = row['parent_bbid']
            if parent_id is None and new.id.bbid is not None:
                # no parent id, top-level line belongs to statement
                parent_id = new.id.bbid.hex

            if parent_id:
                par_id = ID.from_portal(parent_id).bbid
            else:
                par_id = None

            sub_lines = catalog.setdefault(par_id, list())
            sub_lines.append(new_line)

        if catalog:
            def build_line_structure(seed, catalog):
                details = catalog.pop(seed.id.bbid, list())
                for line in details:
                    # IMPORT PDB THIS IS WEIRD
                    old_bbid = line.id.bbid
                    seed.add_line(line, position=line.position, noclear=True)
                    line.id.bbid = old_bbid

                    build_line_structure(line, catalog)

            build_line_structure(new, catalog)

        if catalog:
            import pdb
            pdb.set_trace()

        return new

    def to_portal(self):
        """

        Statement.to_portal() -> dict

        Method yields a serialized representation of self.
        """
        result = {
            'title': self.title,
            'tags': self.tags.to_portal(),
            'bbid': self.id.bbid.hex if self.id.bbid else None
        }

        lines = list()
        for line in self.get_full_ordered():
            top_level = False
            if line.relationships.parent is self:
                top_level = True

            lines.append(line.to_portal(top_level=top_level))

        result['lines'] = lines

        return result
