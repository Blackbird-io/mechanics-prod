# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.data_management
"""

Module defines data structure classes for managing excel interface.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Area                  stores references to a specific area of cells in a
                      worksheet
DriverData            stores driver data for Excel conversion
LineData              holds data for coordinating line location across multiple
                      non-contiguous ranges of rows
Lookup                holds look-up values relative to the starting point
Range                 tracks starting and ending row
Reference             holds reference to a specific line item/cell
RowData               holds row data in dictionary format
SheetData             holds useful data for working with Worksheets
UnitData              holds the Worksheet for a particular BusinessUnit
====================  =========================================================
"""




# Imports
import copy

from bb_exceptions import ExcelPrepError

from .field_names import FieldNames




# Module Globals
field_names = FieldNames()

# Classes
class Area:
    """

    Class stores references to a specific area of cells in an Excel sheet.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    name                  str; name of the instance
    parent                obj; pointer to parent object
    rows                  instance of Lookup(); holds rows in Area
    columns               instance of Lookup(); holds columns in Area

    FUNCTIONS:
    copy()                returns a deep copy of instance
    update()              updates the coordinates of cells within instance
    ====================  =====================================================
    """

    def __init__(self, name=None):
        self.name = name
        self.parent = None

        self.rows = Lookup()
        self.columns = Lookup()

    def copy(self):
        """


        Area.copy() -> Area

        Returns a deep copy of the instance.
        """

        result = copy.copy(self)
        result.rows = self.rows.copy()
        result.columns = self.columns.copy()

        return result

    def update(self, source_area):
        """


        Area.update() -> None

        --``source_area`` must be instance of Area

        Method updates instance.rows and instance.columns to match the
        references in ``source_area``.
        """

        self.rows.update(source_area.rows)
        self.columns.update(source_area.columns)


class DriverData:
    """

    Class stores driver data for Excel conversion.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    rows                  list; contains RowData objects
    formula               str; Excel formula template string
    references            dict; objects keyed by string name
    conversion_map        dict; formula arguments keyed by parameter names
    name                  str; name of driver
    comment               str; comment to include on cell where driver writes
                          data

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """

    def __init__(self):
        self.rows = []
        self.formula = None
        self.references = None
        self.conversion_map = None
        self.name = None
        self.comment = ""


class Range:
    """

    Class for tracking starting and ending row.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    ending                None, CLASS attr
    starting              starting row

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    ending = None
    # To allow property below

    def __init__(self, starting=None):

        self.starting = starting

    # May be starting should be a property, so when you change it, you move
    # all values up or down. Should also get error if its < 1.


class Reference:
    """

    Class for reference line for cell.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    source                source LineItem to use a reference for cell value
    cell                  pointer to cell containing source LineItem in Excel

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    def __init__(self):
        self.source = None
        self.cell = None


class LineData(Range):
    """

    Class for coordinating line location across multiple non-contiguous ranges
    of rows.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    cell                  instance of Cell
    consolidated          instance of Range(); holds consolidation data
                          (list of sources, cell, starting, ending)
    derived               instance of Range(); holds derivation data (list of
                          calculations, cell, starting, ending)
    detailed              instance of Range(); holds detail data (cell,
                          starting, ending)
    reference             instance of Reference
    sheet                 instance of Worksheet

    FUNCTIONS:
    get_coordinates       returns Excel reference string of cell coordinates
    set_sheet             sets instance ``sheet`` attribute
    ====================  =====================================================
    """

    def __init__(self):

        Range.__init__(self)

        self.consolidated = Range()
        self.consolidated.sources = list()
        self.consolidated.labels = list()
        # List should contain pointers to source lines
        self.consolidated.cell = None

        self.derived = Range()
        self.derived.calculations = list()
        # Each item should be a driver_data object
        self.derived.cell = None

        self.detailed = Range()
        self.detailed.cell = None

        self.reference = Reference()

        self.sheet = None
        self.cell = None
        self.number_format = None

    def get_coordinates(self, include_sheet=True):
        """


        LineData.get_coordinates() -> str

        --``include_sheet`` must be a bool; whether or not to return the sheet
            name as part of the coordinate set

        Function returns the coordinates where the line item data was written
        """

        result = None
        if not self.cell:
            raise ExcelPrepError
        else:
            result = ""
            if include_sheet:
                result += "'" + self.cell.parent.title + "'" + "!"
            result += self.cell.coordinate

        return result

    def set_sheet(self, sheet):
        """


        SheetData.set_sheet() -> None

        --``sheet`` must be an instance of Worksheet

        Function sets instance.sheet
        """

        self.sheet = sheet


class Lookup(Range):
    """

    Class for holding look-up values. Values in the lookup are always relative
    to the starting point.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    by_name               dict; lookup table holding values keyed by name
    ending                property; returns last row in range

    FUNCTIONS:
    copy()                returns a deep copy of the instance
    get_position()        returns the relative position of an item
    update()              updates by_name dictionary with supplied values
    ====================  =====================================================
    """

    def __init__(self, *pargs, **kwargs):
        Range.__init__(self, *pargs, **kwargs)
        self.by_name = dict()

    @property
    def ending(self):
        result = None

        if self.by_name:
            starting_value = self.starting or 0
            result = starting_value + max(self.by_name.values())

        return result

    def copy(self):
        """


        Lookup.copy() -> Lookup

        Function returns a deep copy of the instance.
        """

        result = copy.copy(self)
        result.by_name = self.by_name.copy()

        return result

    def get_position(self, name):
        """


        Lookup.get_position() -> int

        --``name`` must be a string

        Function returns the relative position of an item within the lookup
        area.
        """

        first_position = self.starting or 0
        result = first_position + self.by_name[name]

        return result
        # Return natural if starting is blank

    def update(self, source):
        """


        Lookup.update() -> None

        --``source`` must be a dictionary containing key(name)-value pairs to
            be added to or updated in the instance.by_name dict

        Function calls instance.by_name.update() (dictionary method)
        """

        self.by_name.update(source.by_name)


class RowData(dict):
    """

    Class for holding row data in dictionary format.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    field_names           instance of FieldNames; CLASS attr

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """

    field_names = FieldNames()

    def __init__(self):
        self[self.field_names.VALUES] = None
        self[self.field_names.LABELS] = None


class SheetData:
    """

    Class for holding useful data for working with Worksheets.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    general               instance of Area; represents whole sheet
    current_row           int; holds index of the current row in the sheet
    current_column        int; holds index of the current column in the sheet
    consolidation_size    int; number of rows that consolidation area will take
    outline_level         int; holds the outline level for row grouping
    scenario_selector     str; holds string coordinates of selector cell
    sheet                 instance of Worksheet

    FUNCTIONS:
    add_area()            method adds a new area to the worksheet
    set_sheet()           method sets ``sheet`` attribute
    ====================  =====================================================
    """

    def __init__(self):

        self.general = Area()
        self.current_row = None
        self.current_column = None
        self.consolidation_size = None
        self.outline_level = 0
        self.sheet = None
        self.area_names = [field_names.GENERAL]
        self.scenario_selector = None
        self.line_directory = dict()

    def add_area(self, area_name, overwrite=False):
        """


        SheetData.set_sheet() -> Area or None

        --``area_name`` must be the string name for a new area in the worksheet
        --``overwrite`` must be a boolean; whether or not to overwrite if an
            area with the same name already exists

        Function adds a new Area to the instance as an attribute and returns
        the Area.
        """

        result = None
        if getattr(self, area_name, None):

            c = "No implicit overwrites."
            raise Exception(c)

        else:

            new_area = Area(area_name)
            setattr(self, area_name, new_area)
            new_area.parent = self

            result = new_area
            self.area_names.append(area_name)

        return result

    def set_sheet(self, sheet):
        """


        SheetData.set_sheet() -> None

        --``sheet`` must be an instance of Worksheet

        Function sets instance.sheet
        """

        self.sheet = sheet


class UnitData:
    """

    Class for holding the Worksheet for a particular business unit.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    sheet                 instance of Worksheet

    FUNCTIONS:
    set_sheet()           method sets ``sheet`` attr
    ====================  =====================================================
    """

    def __init__(self, sheet=None):
        self.sheet = sheet

    def set_sheet(self, sheet):
        """


        UnitData.set_sheet() -> None

        --``sheet`` must be an instance of Worksheet

        Function sets instance.sheet
        """

        self.sheet = sheet
