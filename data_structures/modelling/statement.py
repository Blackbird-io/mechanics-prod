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
    balance_sheet        bool; whether statement is a balance sheet
    compute              bool; whether to do compute operations on statement
    display_type         str; how to display the statement on the Portal
    visible              bool; whether the statement should be displayed
    
    CLASS DATA:
    COVENANT_TYPE        str; standard name for covenant type declaration
    KPI_TYPE             str; standard name for kpi type declaration
    REGULAR_TYPE         str; standard name for regular type declaration

    FUNCTIONS:
    to_database()         creates a flattened version of Statement for database
    get_monitoring_lines() returns list of monitored lines on the statement
    peer_locator()        returns a function for locating or creating a copy of
                          the instance within a given container
    set_name()            sets instance name and updates ID to reflect the change

    CLASS METHODS:
    from_database()       class method, extracts Statement out of API-format
    ====================  ======================================================
    """
    REGULAR_TYPE = "regular"
    KPI_TYPE = "kpi"
    COVENANT_TYPE = "covenant"

    def __init__(self, name=None, spacing=100, parent=None, period=None,
                 compute=True, balance_sheet=False, visible=True):
        BaseFinancialsComponent.__init__(self, name=name, spacing=spacing,
                                         parent=parent, period=period)
        
        # Display Settings
        self.display_type = self.REGULAR_TYPE
        self.visible = visible

        # Behavioral settings
        self.balance_sheet = balance_sheet  # True if instance is balance sheet
        self.compute = compute  # True to automatically compute statement

    @classmethod
    def from_database(cls, portal_data, financials):
        """

        Statement.from_database(portal_data) -> Statement

        **CLASS METHOD**

        Method extracts a Statement from portal_data.
        """
        new = cls(parent=financials)
        new.tags = Tags.from_database(portal_data['tags'])

        if portal_data['bbid'] is not None:
            new.id.bbid = ID.from_database(portal_data['bbid']).bbid

        # deserialize all LineItems
        catalog = dict()
        for row in portal_data['lines']:
            if row.get('link'):
                new_line = Link.from_database(row, new)
            elif 'driver_id' in row:
                new_line = LineItem.from_database(row, new)
            else:
                new_line = Step.from_database(row)

            parent_id = row.get('parent_bbid', None)
            if parent_id is None and new.id.bbid is not None:
                # no parent id, top-level line belongs to statement
                parent_id = new.id.bbid.hex

            if parent_id:
                par_id = ID.from_database(parent_id).bbid
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

        # DISPLAY TYPE
        stmt_type = portal_data.get("display_type", None)
        if stmt_type and stmt_type != "null":
            new.display_type = stmt_type

        if new.display_type == "regular" and new.name:
            if "covenant" in new.name.casefold():
                new.display_type = new.COVENANT_TYPE

            if "kpi" in new.name.casefold():
                new.display_type = new.KPI_TYPE

        # Visible attribute
        visible = portal_data.get("visible", None)
        if isinstance(visible, bool):
            new.visible = visible

        # Behavioral settings
        compute = portal_data.get("compute", None)
        if compute != "null" and compute is not None:
            new.compute = compute

        balance_sheet = portal_data.get("balance_sheet", None)
        if balance_sheet != "null" and balance_sheet is not None:
            new.balance_sheet = balance_sheet

        return new

    def to_database(self):
        """

        Statement.to_database() -> dict

        Method yields a serialized representation of self.
        """
        result = BaseFinancialsComponent.to_database(self)

        lines = list()
        for line in self.get_full_ordered():
            top_level = False
            if line.relationships.parent is self:
                top_level = True

            lines.append(line.to_database(top_level=top_level))

        result['lines'] = lines
        result['display_type'] = self.display_type
        result['compute'] = self.compute
        result['balance_sheet'] = self.balance_sheet
        result['visible'] = self.visible

        return result

    def copy(self, check_include_details=False, clean=False):
        result = BaseFinancialsComponent.copy(self)
        result.display_type = self.display_type
        result.compute = self.compute
        result.balance_sheet = self.balance_sheet

        return result

    def get_monitoring_lines(self):
        """


        Statement.get_monitoring_lines() -> list

        Method compiles list of monitored lines on the statement and returns
        them.
        """
        out = list()
        for line in self.get_full_ordered():
            if line.usage.monitor:
                out.append(line)

        return out

    def peer_locator(self):
        """


        Statement.peer_locator() -> Statement

        Given a parent container from another time period, return a function
        locating a copy of ourselves within that container.

        Overrides base-class method.
        """

        def locator(financials, **kargs):
            for stub in financials._full_order:
                peer = financials.get_statement(stub)
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
