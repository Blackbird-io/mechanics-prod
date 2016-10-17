# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.unit_fins_chef
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
UnitFinsChef          class containing methods for chopping unit financials
                      into dynamic Excel structures
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
    # n/a

    FUNCTIONS:
    add_financials()      adds dynamic Excel for given financials
    add_valuation_tab()   creates and fills in valuation tab
    ====================  =====================================================
    """
    def __init__(self, model):
        self.model = model
        self.fins_dict = dict()

    def chop_financials(self, sheet, unit):
        """

        UnitChef.add_financials() -> dict

        --``sheet`` must be an instance of openpyxl Worksheet
        --``unit`` must be an instance of BusinessUnit

        Method adds financials to worksheet and returns a dictionary of the
        statements added to the worksheet and their starting rows
        """
        body_rows = sheet.bb.row_axis.get_group('body')
        body_rows.calc_size()
        statement_group = body_rows.add_group(
            'statements',
            offset=1,
        )

        time_line = self.model.get_timeline()
        now = time_line.current_period
        for period in time_line.iter_ordered(open=now.end):
            column = sheet.bb.time_line.columns.get_position(period.end)
            financials = unit.get_financials(period)
            for name, statement in financials.chef_ordered():
                if statement is not None:
                    if name == 'starting':
                        title = 'Starting Balance Sheet'
                        start_bal = True
                    else:
                        title = statement.title
                        start_bal = False

                    line_chef.chop_statement(
                        sheet=sheet,
                        statement=statement,
                        row_container=statement_group,
                        column=column,
                        title=title,
                        start_bal=start_bal,
                    )
                    body_rows.calc_size()

        # We're done with the first pass of chopping financials, now go back
        # and try to resolve problem_line issues.
        while sheet.bb.problem_lines:
            dr_data, materials = sheet.bb.problem_lines.pop()
            line_chef.attempt_reference_resolution(sheet, dr_data, materials)

        return self.fins_dict


    def add_financials(self, sheet, unit, period, column, set_labels=True):
        """

        UnitChef.add_financials() -> None

        --``sheet`` must be an instance of openpyxl Worksheet
        --``unit`` must be an instance of BusinessUnit
        --``column`` must be a column number reference
        --``set_labels`` must be a boolean; True will set labels for line

        Method adds financials to worksheet and returns a dictionary of the
        statements added to the worksheet and their starting rows
        """
        financials = self.model.get_financials(unit.id.bbid, period)
        for name, statement in financials.chef_ordered():
            if statement is not None:
                sheet.bb.current_row += 1
                sheet.bb.outline_level = 0

                statement_row = sheet.bb.current_row + 1

                if name == 'starting':
                    title = 'Starting Balance Sheet'
                    start_bal = True
                else:
                    title = statement.title
                    start_bal = False

                self.fins_dict[title] = statement_row
                statement_rows = self._add_statement_rows(sheet, statement,
                                                          title=title)
                line_chef.chop_statement(
                    sheet=sheet,
                    statement=statement,
                    column=column,
                    row_container=statement_rows,
                    set_labels=set_labels,
                    start_bal=start_bal,
                    title=title,
                )

        # We're done with the first pass of chopping financials, now go back
        # and try to resolve problem_line issues.
        while sheet.bb.problem_lines:
            dr_data, materials = sheet.bb.problem_lines.pop()
            line_chef.attempt_reference_resolution(sheet, dr_data, materials)

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
