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

from .cell_styles import CellStyles
from .line_chef import LineChef
from .sheet_style import SheetStyle
from .unit_info_chef import UnitInfoChef

from chef_settings import VALUATION_TAB_COLOR




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
info_chef = UnitInfoChef()

# Classes
class UnitFinsChef:
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
    MAX_CONSOLIDATION_ROWS = 15
    MAX_LINKS_PER_CELL = 1

    MAX_TITLE_CHARACTERS = 30
    SHOW_GRID_LINES = False
    ZOOM_SCALE = 80

    FUNCTIONS:
    add_items_to_area()   adds dictionary items to specified area
    chop_multi()          returns sheet with a SheetData instance at sheet.bb,
                          also spreads financials, life, parameters of units
    chop_unit()           returns sheet with a SheetData instance at sheet.bb
    ====================  =====================================================
    """
    def add_financials(self, *pargs, sheet, unit, column, set_labels=True):
        """

        UnitChef._add_financials() -> dict

        Method adds financials to worksheet and returns a dictionary of the
        statements added to the worksheet and their starting rows
        """
        fins_dict = dict()

        body_rows = sheet.bb.row_axis.get_group('body')
        body_rows.add_group(
            'statements',
            offset=sheet.bb.current_row - body_rows.tip + 1
        )

        for statement in unit.financials.ordered:
            if statement is not None:
                sheet.bb.current_row += 1
                sheet.bb.outline_level = 0

                if statement is unit.financials.ending:
                    statement_row = sheet.bb.current_row + 1
                    fins_dict["Starting Balance Sheet"] = statement_row

                    statement_rows = self._add_statement_rows(
                        sheet, statement, title='Starting Balance Sheet'
                    )
                    line_chef.chop_starting_balance(
                        sheet=sheet,
                        unit=unit,
                        column=column,
                        row_container=statement_rows,
                        set_labels=set_labels
                    )
                    sheet.bb.need_spacer = False

                statement_row = sheet.bb.current_row + 1
                fins_dict[statement.tags.name] = statement_row

                statement_rows = self._add_statement_rows(sheet, statement)
                line_chef.chop_statement(
                    sheet=sheet,
                    statement=statement,
                    column=column,
                    row_container=statement_rows,
                    set_labels=set_labels,
                )

        # We're done with the first pass of chopping financials, now go back
        # and try to resolve problem_line issues.
        while sheet.bb.problem_lines:
            dr_data, materials = sheet.bb.problem_lines.pop()
            line_chef.attempt_reference_resolution(sheet, dr_data, materials)

        return fins_dict

    @staticmethod
    def add_valuation_tab(book, unit, index=None):
        """


        UnitChef._add_valuation_tab() -> Worksheet

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit

        Method creates a valuation tab and chops unit valuation statement.
        """

        # 1.0   set up the unit sheet and spread params
        if not index:
            index = len(book.worksheets)

        if index == 2:
            name = "Valuation"
        else:
            name = unit.name + ' val'

        sheet = info_chef.create_unit_sheet(book=book, unit=unit,
                                        index=index, name=name,
                                        current_only=True)

        sheet.bb.outline_level += 1

        # 1.1   set-up life
        sheet.bb.current_row += 1
        sheet = info_chef.add_unit_life(sheet=sheet, unit=unit)
        sheet.bb.outline_level -= 1

        # 1.2  Add Valuation statement
        sheet.bb.current_row = sheet.bb.events.rows.ending
        sheet.bb.current_row += 1

        current = sheet.bb.time_line.columns.get_position(unit.period.end)
        SheetStyle.set_column_width(sheet, current, width=22)

        statement_row = sheet.bb.current_row + 1
        statement = unit.financials.valuation
        line_chef.chop_statement(
            sheet=sheet,
            statement=statement,
            column=current,
            set_labels=True)

        # 1.5 add area and statement labels and sheet formatting
        SheetStyle.style_sheet(sheet)
        CellStyles.format_area_label(sheet, statement.name, statement_row)

        # # 1.6 add selector cell
        #   Make scenario label cells
        info_chef.add_scenario_selector_logic(book, sheet)

        sheet.sheet_properties.tabColor = VALUATION_TAB_COLOR

        return sheet

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                              #
    # *************************************************************************#
    def _add_statement_rows(self, sheet, statement, title=None):
        """

        UnitChef._add_statement() -> AxisGroup

        """
        statement_group = sheet.bb.row_axis.get_group('body', 'statements')
        statement_group.calc_size()

        offset = 1 if statement_group.size else 0
        name = title or statement.name
        statement_rows = statement_group.add_group(name, offset=offset)
        statement_rows.add_group('title', title=name, size=1)
        statement_rows.add_group('matter', size=0)

        return statement_rows
