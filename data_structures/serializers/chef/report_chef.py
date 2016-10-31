# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.report_chef
"""

Class for creating dynamic Excel reports showing forecast and actual values.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ReportChef            class to generate reports from forecast and actual values
====================  =========================================================
"""




# Imports
import os
import openpyxl as xlio

import bb_settings
from .cell_styles import CellStyles
from .garnish_chef import GarnishChef
from .line_chef import LineChef
from .transcript_chef import TranscriptChef
from .unit_chef import UnitChef
from .summary_chef import SummaryChef
from .unit_structure import StructureChef




# Constants
# N/A

# Module Globals
# N/A

# Classes
class ReportChef:
    """

    Class packages an Engine model containing forecast and actual values into
    and Excel workbook containing reports for the specified dates (or all) 
    with dynamic links and (someday) graphics and analysis.
    ==============  ===========================================================
    Attribute             Description
    ==============  ===========================================================

    DATA:
    end_date        datetime.date; last date for which to make reports
    model           obj; instance of blackbird model
    spec_dates      bool; make reports for all available dates (False) or 
                    specific dates (True)
    st_date         datetime.date; first date for which to make reports

    FUNCTIONS:
    build_reports()  method builds reports within date range
    add_report()     method adds a specific report
    ===============  ==========================================================
    """

    def __init__(self, model, dates=None):
        self.model = model

        if self.dates is not None:
            self.spec_dates = True
            self.start_date = min(dates)
            self.end_date = max(dates)
        else:
            self.spec_dates = False
            self.start_date = min(self.actual.keys())
            self.end_date = max(self.actual.keys())

        # ****Formatting information****
        # where statement names are written
        self._stat_label_column = 3  # 'C'
        self._line_lable_column = 4  # 'D'

        # Where title is written
        self._banner_row = 3
        self._banner_col_st = 3  # 'C'
        self._banner_col_ed = 8  # 'H'
        self._banner_color = 'NAVY'  # RGB(0, 32, 96)
        # self.banner_font = Font(bold=True, color=WHITE)

        # Where column headers are written
        self._header_row = 6

        self._forecast_col = 5  # 'E'
        self._actual_col = 6  # 'F'
        self._delta_col = 7  # 'G'
        self._diff_col = 8  # 'H'
        
        self._placeholder = '--'  # value to use in reports for Divide by Zero 
                                 # error or unavailable data

    def build_reports(self, wb, forecast, actual):
        """
        At this point, the "Forecast" and "Actual" tabs will already exist,
        so we can access cell coordinates.

        actual_periods = sorted(actual.values(), keyed by .start)
        for act_period in actual_periods:
            if act_period.start >= self.start_date and act_period.end <= self.end_date:
                for_period = forecast.find_period(actual_period.end)

                self.add_report(wb, act_period, for_period)


            elif act_period.end > self.end_date:
                break # since we sorted keys first, we know we won't want
                      # any future periods

        """

        pass

    def add_report(self, wb, act_period, for_period):
        """

        sheet = wb.create_sheet()
        self._make_report_header(sheet, act_period)

        co = self.model.get_company()

        act_fins = self.model.get_financials(co.id.bbid, act_period)
        for_fins = self.model.get_financials(co.id.bbid, for_period)

        # Try to use row container, figure out how it works

        for name, act_statement in act_fins.full_ordered():
            for_statement = getattr(for_fins, name)
            self._report_statement(sheet, act_statement, for_statement)

        CellStyles.add_border_box()

        add bounding box around report (thin outside border):
            - self.stat_label_column-1 to self.diff_col+1
            - self.banner_row-1 to current_row + 1
        """
        pass

    def _make_report_header(self, sheet, act_period):
        """
        Add header formatting:
        - Join cells C3:H3
        - Set date label ("Date of collection:" in cell C5 (bold, aligned left)
        - Set date value (end of actual period?)
        - Set header cells:
            - bottom border: thin
            - font: bold
            - alignment: center
            Forecast: E6
            Actual: F6
            Delta: G6
            Percent Difference: H6
        -  Set column widths:
            B: 2.4
            I: 2.4
            C thru H: 16.63
        """
        pass

    def _report_statement(self, sheet, act_statement, for_statement):
        """

        cell = sheet.cell(row=current_row, column=self.label_column)
        CellStyle.format_statement_label()

        for act_line in act_statement.get_ordered():
            for_line = for_statement.find_first(act_line.name)
        """
        pass

    def _report_line(self, sheet, act_line, for_line):
        """
        if act_line._details:
            for det_act_line in act_line._details:
                det_for_line = for_line.find_first(det_act_line.name)
                self._report_line(sheet, det_act_line, det_for_line, indent=bigger indent)

            # Copy soem logic from line chef

        else:
            # Don't need to worry about calcs, etc. here, we're just
            referencing the cell where it was written

            - print line name
            - set reference to Forecast cell
            - set reference to Actual cell
            - set formula for Delta cell (Actual cell - Forecast cell)
            - set formula for Percent Difference cell (=IFERROR((Actual Cell - Forecast Cell )/ Forecast Cell, self.placeholder)
        """
        pass
