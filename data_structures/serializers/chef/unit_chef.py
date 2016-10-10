# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.unit_chef
"""

Module defines a class that represents arbitrarily rich BusinessUnit instances
as a collection of linked Excel worksheets.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
UnitChef              class containing methods to chop BusinessUnits into
                      dynamic Excel structures
====================  =========================================================
"""




# Imports
import openpyxl as xlio

from ._chef_tools import group_lines
from .cell_styles import CellStyles
from .line_chef import LineChef
from .sheet_style import SheetStyle
from .unit_fins_chef import UnitFinsChef
from .unit_info_chef import UnitInfoChef

from chef_settings import (
    SCENARIO_SELECTORS, VALUATION_TAB_COLOR, HIDE_LIFE_EVENTS,
    APPLY_COLOR_TO_DECEMBER, DECEMBER_COLOR,
)
from openpyxl.styles import PatternFill




# Constants
# n/a

# Module Globals
_INVALID_CHARS = r"\/*[]:?"
# Excel forbids the use of these in sheet names.
REPLACEMENT_CHAR = None
# When the replacement character is None, UnitChef will remove all bad chars
# from sheet titles.
bad_char_table = {ord(c): REPLACEMENT_CHAR for c in _INVALID_CHARS}
get_column_letter = xlio.utils.get_column_letter
line_chef = LineChef()
fins_chef = UnitFinsChef()
info_chef = UnitInfoChef()

# Classes
class UnitChef:
    """

    One tab per unit
    Children first
    Arbitrarily recursive (though should max out at sheet limit; alternatively,
    book should prohibit new sheets after that? or can have 2 limits: a soft
    limit where ModelChopper shifts into different representation mode, and a
    hard limit, where you just cant create any more sheets.)

    Most non-public methods force keyword-based arg entry to avoid potentially
    confusing erros (switching rows for columns, etc.)

    Methods generally leave current row pointing to their last completed
    (filled) row.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    chop_multi()          returns sheet with a SheetData instance at sheet.bb,
                          also spreads financials, life, parameters of units
    chop_multi_valuation() returns sheet with a SheetData instance at sheet.bb,
                          makes and fills Valuation tab
    ====================  =====================================================
    """
    def chop_multi(self, *pargs, book, unit):
        """


        UnitChef.chop_multi() -> Worksheet

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit

        Method recursively walks through ``unit`` and components and chops them
        into Excel format.  Method also spreads financials, parameters, and
        life of the unit.
        """

        # 1.   Chop the children
        before_kids = len(book.worksheets)
        children = unit.components.get_ordered()

        for child in children:
            self.chop_multi(book=book, unit=child)

        # 2.   Chop the parent
        #
        # In this block, we have to set the current row to the place where the
        # last area ends before running the breadth-wise routines. Otherwise,
        # they would treat the ending row of the last period as their own
        # starting row, and the spreadsheet would look like a staircase.

        # 2.1.   set up the unit sheet and spread params
        sheet = info_chef.create_unit_sheet(book=book, unit=unit,
                                        index=before_kids)
        sheet.bb.outline_level += 1

        # 2.2.   spread life
        info_chef.unit_life(sheet, unit)

        # 2.3. add unit size
        sheet.bb.current_row += 2
        info_chef.add_unit_size(sheet=sheet, unit=unit, set_labels=True)
        for snapshot in unit:
            sheet.bb.current_row = sheet.bb.size.rows.ending
            info_chef.add_unit_size(sheet=sheet, unit=snapshot, set_labels=False)

        sheet.bb.outline_level += 1
        group_lines(sheet, sheet.bb.size.rows.ending)
        sheet.bb.outline_level -= 1

        # 2.4.  spread fins
        current = sheet.bb.time_line.columns.get_position(unit.period.end)
        fins_dict = fins_chef.add_financials(sheet=sheet, unit=unit,
                                             column=current)

        for snapshot in unit:
            sheet.bb.current_row = sheet.bb.size.rows.ending
            column = sheet.bb.time_line.columns.get_position(
                snapshot.period.end)
            # Load balance from prior column!!!

            fins_chef.add_financials(sheet=sheet, unit=snapshot, column=column,
                                     set_labels=False)

            # Should make sure rows align here from one period to the next.
            # Main problem lies in consolidation logic.

        # 2.5 add area and statement labels and sheet formatting
        SheetStyle.style_sheet(sheet)

        for statement, row in fins_dict.items():
            CellStyles.format_area_label(sheet, statement, row)

        # # 2.6 add selector cell
        #   Make scenario label cells
        info_chef.add_scenario_selector_logic(book, sheet)

        # Color the December columns
        if APPLY_COLOR_TO_DECEMBER:
            for date, column in sheet.bb.time_line.columns.by_name.items():
                if date.month == 12:
                    for row in range(1, sheet.max_row + 1):
                        cell = sheet.cell(column=column, row=row)
                        cell.fill = PatternFill(start_color=DECEMBER_COLOR,
                                                end_color=DECEMBER_COLOR,
                                                fill_type='solid')

        return sheet

    def chop_multi_valuation(self, *pargs, book, unit, index, recur=False):
        """


        UnitChef.chop_multi_valuation() -> Worksheet

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit
        --``index`` is optionally the index at which to insert the tab
        --``recur`` bool; whether to chop valuation for lower units

        Method recursively walks through ``unit`` and components and will chop
        their valuation if any exists.
        """

        # 1.   Chop the children
        if recur:
            children = unit.components.get_ordered()

            for child in children:
                index = book.get_index(child.xl.sheet) - 1
                self.chop_multi_valuation(book=book, unit=child,
                                          index=index, recur=recur)

        # 2.6 add valuation tab, if any exists for unit
        if unit.financials.has_valuation:
            fins_chef.add_valuation_tab(book, unit, index=index)
