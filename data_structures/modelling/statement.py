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
from data_structures.guidance.step import Step
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
    Statement is BaseFinancialsComponent that collects structured LineItems.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    N/A

    FUNCTIONS:
    to_portal()           creates a flattened version of Statement for Portal
    peer_locator()        returns a function for locating or creating a copy of
                          the instance within a given container
    set_name()            sets instance name and updates ID to reflect the change

    CLASS METHODS:
    from_portal()         class method, extracts Statement out of API-format
    ====================  ======================================================
    """

    def __init__(self, name=None, spacing=100, parent=None, period=None):
        BaseFinancialsComponent.__init__(self, name=name, spacing=spacing,
                                         parent=parent, period=period)

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
            elif 'driver_id' in row:
                new_line = LineItem.from_portal(row, new)
            else:
                new_line = Step.from_portal(row)

            parent_id = row.get('parent_bbid', None)
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
                    old_bbid = line.id.bbid
                    position = getattr(line, 'position', None)
                    seed.add_line(line, position=position, noclear=True)
                    line.id.bbid = old_bbid

                    build_line_structure(line, catalog)

            build_line_structure(new, catalog)

        return new

    def to_portal(self):
        """

        Statement.to_portal() -> dict

        Method yields a serialized representation of self.
        """
        result = BaseFinancialsComponent.to_portal(self)

        lines = list()
        for line in self.get_full_ordered():
            top_level = False
            if line.relationships.parent is self:
                top_level = True

            lines.append(line.to_portal(top_level=top_level))

        result['lines'] = lines

        return result

    def peer_locator(self):
        """


        Statement.peer_locator() -> Statement

        Given a parent container from another time period, return a function
        locating a copy of ourselves within that container.

        Overrides base-class method.
        """

        def locator(financials, **kargs):
            for stub in financials._full_order:
                peer = getattr(financials, stub)
                if peer.name == self.name:
                    return peer

        return locator

    def set_name(self, name):
        """


        Statement.set_name() -> None

        --``name`` is the string name to assign to the Statement

        Method sets the name on the Statement and updates its ID with to
        reflect the name change.

        Delegates to base-class method.
        """
        BaseFinancialsComponent.set_name(self, name)
        self.register(self.id.namespace)
