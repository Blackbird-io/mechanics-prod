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

from .line_chef import LineChef




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
    add_statement_container() adds a row group to hold a statement
    ====================  =====================================================
    """
    def __init__(self, model, timeline):
        self.model = model
        self.fins_dict = dict()
        self.timeline = timeline

    def chop_financials(self, sheet, unit, values_only=False):
        """

        UnitChef.add_financials() -> dict

        --``sheet`` must be an instance of openpyxl Worksheet
        --``unit`` must be an instance of BusinessUnit

        Method adds financials to worksheet and returns a dictionary of the
        statements added to the worksheet and their starting rows
        """
        line_chef = LineChef(values_only)

        now = getattr(self.timeline, 'current_period', None)
        if now is None:
            now = self.timeline[min(self.timeline.keys())]

        for period in self.timeline.iter_ordered(open=now.end):
            if period.start < now.start:
                continue

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
                    statement_rows = self.add_statement_container(
                        sheet, statement, title=title
                    )
                    line_chef.chop_statement(
                        sheet=sheet,
                        statement=statement,
                        row_container=statement_rows,
                        column=column,
                        title=title,
                        start_bal=start_bal,
                        set_labels=(period.end == now.end),
                    )

        # We're done with the first pass of chopping financials, now go back
        # and try to resolve problem_line issues.
        while sheet.bb.problem_lines:
            dr_data, materials = sheet.bb.problem_lines.pop()
            line_chef.attempt_reference_resolution(sheet, dr_data, materials)

        return self.fins_dict

    def add_statement_container(self, sheet, statement, title=None):
        """

        UnitChef._add_statement() -> AxisGroup

        Adds row container for a statement, with a title and lines placeholder.
        """
        body_rows = sheet.bb.row_axis.get_group('body')
        body_rows.calc_size()
        statement_group = body_rows.add_group('statements', offset=1)

        offset = 1 if statement_group.size else 0
        label = title or statement.title
        statement_rows = statement_group.add_group(label, offset=offset)
        statement_rows.add_group('title', size=1, rank=1, label=label)
        statement_rows.add_group('lines')

        return statement_rows
