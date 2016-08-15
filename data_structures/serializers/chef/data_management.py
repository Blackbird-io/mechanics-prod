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
LineFormat            holds formatting for lines in Excel
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

from openpyxl.styles import Side
from openpyxl.utils import get_column_letter

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
        # Cells created from consolidation sources
        self.consolidated.array = []

        self.derived = Range()
        self.derived.calculations = list()
        # Each item should be a driver_data object
        self.derived.cell = None

        self.detailed = Range()
        self.detailed.cell = None

        self.reference = Reference()

        self.sheet = None
        self.cell = None
        self.format = LineFormat()

    @property
    def number_format(self):
        """
        legacy interface
        """
        return self.format.number_format

    @number_format.setter
    def number_format(self, value):
        self.format.number_format = value

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


class LineFormat:
    """

    Class for formatting line values in Excel.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    blank_row_after       bool; insert a blank row after writing line
    blank_row_before      bool; insert a blank row before writing line
    border                str; name of an openpyxl border style
                         (openpyxl.styles.Side.style.values)
    font_format           dict; contains openpyxl-compatible Font kwargs
    number_format         None or an openpyxl number format

    FUNCTIONS:
    N/A
    ====================  =====================================================
    """
    def __init__(self):
        self.number_format = None
        self.blank_row_before = False
        self.blank_row_after = False
        self._border = None

        # will accept any additional format items for font/text format;
        # anything that conforms to opynpyxl.styles.Font keywords will
        # work to format values/text as expected
        self.font_format = dict()

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value):
        try:
            assert value in Side.style.values
        except AssertionError:
            c = "Border value must be in openpyxl.styles.Side.style.values. " \
                "Common values are 'thin','medium','thick', 'dotted', etc."
            raise ValueError(c)
        else:
            self._border = value

    @border.deleter
    def border(self):
        self._border = None

    def copy(self):
        """


        LineFormat.copy() -> obj

        Function makes a copy of instance and returns it.
        """
        result = LineFormat()
        result.number_format = self.number_format
        result.blank_row_after = self.blank_row_after
        result.blank_row_before = self.blank_row_before
        result._border = self._border
        result.font_format = self.font_format.copy()

        return result

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
    problem_lines         list; temp storage for lines with reference problems
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
        self.problem_lines = []

        self.row_axis = AxisGroup(tip=0)
        self.col_axis = AxisGroup(tip=0)

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


class AxisGroup:
    """

    A placeholder for spreadsheet layout on the R and C axes. Defines the order
    of rows or cols without specifying their exact location at first.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    name                  our tag, unique within parent
    path                  shows path to ourselves from the very top
    offset                our offset from the predecessor, or from the tip of
                          container if we are at the top of container
    tip                   0-base starting position of this group in container
                          after offset is applied, may be None if unknown
    size                  total span from tip to end, fixed or calculated,
                          does not include own offset
    outline               Excel outline level for group
    groups                ordered container for groups
    by_name               unique names of groups -> index in groups
    extra                 anything else we need to remember

    FUNCTIONS:
    add_group()           recursively adds nested groups or returns existing
    get_group()           same as add_group, but will not add
    calc_size()           calculates the span of this group and children
    get_subgroups()       convenience iterator over subgroups
    number()              converts 0 -> 1 for Excel coordinate system
    get_corner_address()  converts row and col coordinates into 'A1' for Excel
    ====================  =====================================================
    """
    def __init__(self, **kargs):
        """

        AxisGroup.__init__() -> None

        Any unparsed (key, value) pairs in kargs will be placed into the
        ``extra`` dict, to facilitate manipulation and formatting.
        """
        self.tip = kargs.get('tip')
        self.name = kargs.get('name')
        self.path = kargs.get('path')
        self.size = kargs.get('size')
        self.offset = kargs.get('offset')
        self.outline = kargs.get('outline', 0)
        self.groups = []
        self.by_name = {}

        # any extra information, e.g. labels
        self.extra = {}
        for k, v in kargs.items():
            if k not in self.__dict__:
                self.extra[k] = v

    def add_group(
        self, *path, size=None, offset=None, add_outline=False, **kargs
    ):
        """

        AxisGroup.add_group() -> AxisGroup

        Walks the ``path`` adding groups at nested levels, or matching existing
        ones.
        """
        group = self

        for name in path:
            # anyting that formats will do as a tag
            name = format(name)

            if name in group.by_name:
                group_idx = group.by_name[name]
                group = group.groups[group_idx]
            else:
                new_group = self._make_group(
                    name, size, offset, add_outline, **kargs
                )
                group.by_name[name] = len(group.groups)
                group.groups.append(new_group)
                group = new_group
        return group

    def get_group(self, *path):
        """

        AxisGroup.add_group() -> None

        Walks the ``path`` to match an existing group, returns None if not
        found (instead of creating one as add_group would do).
        """
        group = self
        for name in path:
            name = format(name)
            if name in group.by_name:
                group_idx = group.by_name[name]
                group = group.groups[group_idx]
            else:
                return None
        return group

    def calc_size(self, render=None):
        """

        AxisGroup.calc_size() -> int

        --``render`` callable to apply to each subgroup

        Recursively calculates and sets the span sizes of all subgroups.
        Only works if own tip is set.
        Group size is the sum of subgroup sizes and their offsets.
        Own offset is not included in own size, but added to parent's size.
        Will adjusts the starting locations of groups based on predecessor's
        sizes.
        """
        mysize = 0
        for group in self.groups:
            group.tip = self.tip + mysize + (group.offset or 0)
            if group.groups:
                group_size = group.calc_size(render=render)
            else:
                # group without subgroups or size is allowed, counts as empty
                group_size = group.size or 0
            # accumulate subgroup sizes into mysize
            mysize += group_size + (group.offset or 0)
            # if a callback is given, apply it to this group
            if render:
                render(group)
        # if all subgroups are empty, turn to self.size
        if not mysize:
            mysize = self.size or 0
        self.size = mysize
        return mysize

    def get_subgroups(self, name):
        """

        AxisGroup.get_subgroups() -> iter -> AxisGroup

        Convenience iterator over the subgroups of a group given by ``name``.
        """
        if name in self.by_name:
            group_idx = self.by_name[name]
            for group in self.groups[group_idx].groups:
                yield group

    def find_all(self, *path):
        """

        AxisGroup.find_all() -> iter -> AxisGroup

        Convenience iterator over the subgroups at a certain level in the path.
        If None is in the path, all groups are returned at that level.
        To iterate over all terminal groups in the ``path``, conclude ``path``
        with None.
        """
        if path:
            name = path[0]
            for group in self.groups:
                if name is not None and group.name != format(name):
                    continue
                if len(path) > 1:
                    yield from group.find_all(*path[1:])
                else:
                    yield group

    def number(self):
        """

        AxisGroup.number() -> int

        Excel convenience: converts own 0-base location into 1-base.
        """
        if self.tip is not None:
            return self.tip + 1

    def get_corner_address(self, col_group, row_path=[], col_path=[]):
        """

        AxisGroup.get_corner_address() -> str

        --``col_group`` AxisGroup, column locator

        Excel convenience: finds the address label of our intersection with
        a column locator (top left cell address), e.g. 'C9'.
        Only makes sense if we are a row locator, and the cross-locator is a
        column locator.
        """
        row = self.get_group(*row_path)
        col = col_group.get_group(*col_path)
        if row and col:
            rownum = row.number()
            colnum = col.number()
            letter = get_column_letter(colnum)
            return '{}{}'.format(letter, rownum)

    def get_range_address(self, col_group, row_path=[], col_path=[]):
        """

        AxisGroup.get_corner_address() -> str

        --``col_group`` AxisGroup, column locator

        Excel convenience: finds the full range address of our intersection
        with a column locator, e.g. 'C2:E9'. Sizes need to be set.
        Only makes sense if we are a row locator, and the cross-locator is a
        column locator.
        """
        row = self.get_group(*row_path)
        col = col_group.get_group(*col_path)
        if row and col:
            rowtip = row.number()
            rowend = row.number() + row.size - 1
            coltip = col.number()
            colend = col.number() + col.size - 1
            coltip = get_column_letter(coltip)
            colend = get_column_letter(colend)
            return '{}{}:{}{}'.format(coltip, rowtip, colend, rowend)

    def get_span(self, *path, letters=False):
        """

        AxisGroup.get_span() -> (int, int) or (str, str)

        --``letters`` return column letters instead of numbers

        Excel convenience: first and last row/col numbers of the Excel range
        spanned by us. As column letters, optionally.
        Breaks if size has not been set.
        """
        group = self.get_group(*path)
        tip = group.tip + 1
        end = group.tip + group.size
        if letters:
            tip = get_column_letter(tip)
            end = get_column_letter(end)
        return tip, end

    #**************************************************************************#
    #                          NON-PUBLIC METHODS                              #
    #**************************************************************************#

    def _make_group(self,
        name, size=None, offset=None, add_outline=False, **kargs
    ):
        """

        AxisGroup._make_group() -> AxisGroup

        Constructs AxisGroup instance parameters from inputs. Does some of the
        work of .calc_size(), for cases when span can be calculated at
        construction time.
        """
        name = format(name)

        # decorative property, for debugging
        path = name
        if self.path:
            path = self.path + '.' + path

        # child's head position, if we can tell what it is
        tip = None
        if self.groups:
            # from peer predecessor
            end_group = self.groups[-1]
            if end_group.tip is not None and end_group.size is not None:
                tip = end_group.tip + end_group.size
        elif self.tip is not None:
            # from container
            tip = self.tip

        # shift the starting position, creating an implicit spacer
        if tip is not None and offset:
            tip += offset

        # bump up outline level by one, if set
        outline_level = (self.outline or 0)
        if add_outline:
            outline_level += 1

        new_group = AxisGroup(
            name=name,
            path=path,
            tip=tip,
            size=size,
            offset=offset,
            outline=outline_level,
            **kargs
        )
        return new_group
