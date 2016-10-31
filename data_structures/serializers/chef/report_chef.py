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
from openpyxl.utils import get_column_letter

from .cell_styles import CellStyles
from .sheet_style import SheetStyle




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

    def __init__(self, model, proj, actl, dates=None):
        self.model = model
        self.forecast = proj
        self.actual = actl

        if dates is not None:
            self.spec_dates = True
            self.start_date = min(dates)
            self.end_date = max(dates)
        else:
            self.spec_dates = False
            self.start_date = min(self.actual.keys())
            self.end_date = max(self.actual.keys())

        self._placeholder = '--'  # value to use in reports for Divide by Zero 
                                 # error or unavailable data

    def build_reports(self, wb):
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
        actual_periods = sorted(self.actual.values(), key=lambda x: x.start)

        for act_period in actual_periods:
            if act_period.start >= self.start_date and act_period.end <= self.end_date:
                for_period = self.forecast.find_period(act_period.end)

                self.add_report(wb, act_period, for_period)

            elif act_period.end > self.end_date:
                # since we sorted keys first, we know we won't want
                # any future periods
                break

    def add_report(self, wb, act_period, for_period):
        """
        lasdkjflkajds
        """
        # Do preliminary formatting
        use_date = act_period.end
        tab_name = use_date.strftime('%Y-%m-%d')
        title = '%s: %s Performance' % (self.model.title, use_date.strftime('%m-%Y'))
        sheet = wb.create_sheet(tab_name, index=1)
        self._make_report_header(sheet, title, use_date)

        co = self.model.get_company()

        act_fins = self.model.get_financials(co.id.bbid, act_period)
        for_fins = self.model.get_financials(co.id.bbid, for_period)

        for name, act_statement in act_fins.chef_ordered():
            if act_statement is not None:
                for_statement = getattr(for_fins, name)
                self._report_statement(sheet, act_statement, for_statement)

        # Add Finishing Touches
        sheet.bb.calc_sizes()

        all_col = sheet.bb.col_axis.get_group('all')
        st_col = all_col.get_group('space_left').number()
        ed_col = all_col.get_group('space_right').number()

        all_row = sheet.bb.row_axis.get_group('all')
        st_row = all_row.number()
        ed_row = st_row + all_row.size

        CellStyles.format_border_group(sheet, st_col, ed_col, st_row, ed_row)

        sheet.parent.save(r'C:\Blackbird\test_reporting.xlsx')
        import pdb
        pdb.set_trace()

    def _make_report_header(self, sheet, title, date):
        """
        Add header
        """
        sheet.sheet_properties.tabColor = 'FFFFFF'
        SheetStyle.style_sheet(sheet)

        all_rows = sheet.bb.row_axis.add_group('all', offset=1)
        all_cols = sheet.bb.col_axis.add_group('all', size=8, offset=1)

        #  set up rows
        ban_row = all_rows.add_group('banner', size=1, offset=1)
        date_row = all_rows.add_group('report_date', size=1, offset=1)
        header_row = all_rows.add_group('column_headers', size=1)

        # set up columns
        space_left = all_cols.add_group('space_left', size=1)
        label_col = all_cols.add_group('labels', size=1)
        line_col = all_cols.add_group('lines', size=1)
        fore_col = all_cols.add_group('Forecast', size=1)
        actl_col = all_cols.add_group('Actual', size=1)
        delta_col = all_cols.add_group('Delta', size=1)
        perc_diff = all_cols.add_group('Percent Difference', size=1)
        space_right = all_cols.add_group('space_right', size=1)

        sheet.bb.calc_sizes()

        # Make Banner Cell
        # Get furthest left banner cell and format as desired
        banner_cell = sheet.cell(row=ban_row.number(), column=label_col.number())
        banner_cell.value = title
        CellStyles.format_header_label(banner_cell, alignment='center',
                                       color='002060', font_color='FFFFFF',
                                       bold=True, font_size=16, name='Arial')

        # merge banner cells
        st_col = get_column_letter(label_col.number())
        ed_col = get_column_letter(perc_diff.number())
        row_num = ban_row.number()
        merge_range = '%s%s:%s%s' % (st_col, row_num, ed_col, row_num)
        sheet.merge_cells(merge_range)

        # Set date cell (should just be its own row/col group with offset = 1)
        label_cell = sheet.cell(row=date_row.number(), column=label_col.number())
        label_cell.value = 'Date of collection:'
        CellStyles.format_bold(label_cell)

        value_cell = sheet.cell(row=date_row.number(), column=line_col.number())
        value_cell.value = date
        CellStyles.format_date(value_cell)
        CellStyles.format_bold(value_cell)

        # Set header columns (should be own row group w/offset=1, col group with offset=3)
        groups = [fore_col, actl_col, delta_col, perc_diff]
        for col in groups:
            cell = sheet.cell(row=header_row.number(), column=col.number())
            cell.value = col.name
            CellStyles.format_header_label(cell, alignment='center',
                                           color='00FFFFFF',
                                           font_color="000000")
            CellStyles.format_border(cell, bottom=True)

        # Set Column Widths
        SheetStyle.set_column_width(sheet, space_left.number(), 2.4)
        SheetStyle.set_column_width(sheet, space_right.number(), 2.4)
        for c in range(label_col.number(), perc_diff.number()+1):
            SheetStyle.set_column_width(sheet, c, 16.63)

    def _report_statement(self, sheet, act_statement, for_statement):
        """
        Add report statements
        """
        all_cols = sheet.bb.col_axis.get_group('all')
        lab_col = all_cols.get_group('labels')

        all_rows = sheet.bb.row_axis.get_group('all')
        stat_rows = all_rows.add_group(act_statement.name, offset=1)
        lab_row = stat_rows.add_group('label', size=1)
        sheet.bb.calc_sizes()

        cell = sheet.cell(row=lab_row.number(), column=lab_col.number())
        cell.value = act_statement.title.title()
        CellStyles.format_bold(cell)

        for act_line in act_statement.get_ordered():
            for_line = for_statement.find_first(act_line.name)

            self._report_line(sheet, act_line, for_line, stat_rows)

        sheet.bb.calc_sizes()

    def _report_line(self, sheet, act_line, for_line, row_container):
        """
        all_cols = sheet.bb.col_axis.get_group('all')
        line_col = all_cols.get_group('line_col')
        forecast_col = all_cols.get_group('Forecast')
        actual_col = all_cols.get_group('Actual')
        delta_col = all_cols.get_group('Delta')
        diff_col = all_cols.get_group('Percent Difference')

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
        import pdb
        pdb.set_trace()

        pass
