# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.model_chef
"""

Class for creating dynamic Excel representations of Blackbird Engine models.

Chef modules write formulas to cells explicitly, using the set_explicit_value()
method, to make sure Excel interprets the strings correctly.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
field_names           commonly used field names
formula_templates     string templates for commonly used formulas
tab_names             standard tab names

FUNCTIONS:
n/a

CLASSES:
ModelChef             chop Blackbird Engine model into a dynamic Excel workbook
====================  =========================================================
"""




# Imports
import os
import openpyxl as xlio
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.styles.colors import WHITE, BLACK

import bb_settings
import chef_settings
from chef_settings import SCENARIO_SELECTORS
from ._chef_tools import add_scenario_selector
from .bb_workbook import BB_Workbook as Workbook
from .cell_styles import CellStyles
from .data_types import TypeCodes
from .field_names import FieldNames
from .formulas import FormulaTemplates
from .line_chef import LineChef
from .sheet_style import SheetStyle
from .tab_names import TabNames
from .unit_chef import UnitChef




# Constants
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'static', 'blackbird_engine_2X_410x120.png')

# Module Globals
cell_styles = CellStyles()
field_names = FieldNames()
formula_templates = FormulaTemplates()
line_chef = LineChef()
sheet_style = SheetStyle()
tab_names = TabNames()
type_codes = TypeCodes()
unit_chef = UnitChef()

get_column_letter = xlio.utils.get_column_letter
bounding_box = xlio.drawing.image.bounding_box

# Classes
class ModelChef:
    """

    Class packages an Engine model into an Excel workbook with dynamic links.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    chop_model()          returns BB_Workbook containing an Excel workbook with
                          dynamic links
    ====================  =====================================================
    """

    def chop_model(self, model):
        """


        ModelChef.chop_model -> BB_Workbook

        --``model`` is an instance of Blackbird Engine model

        Method delegates to UnitChef to chop BusinessUnits and returns an
        instance of BB_Workbook.  BB_Workbook contains an Excel workbook with
        dynamic links.
        """

        book = self._build_foundation(model)
        now = model.time_line.current_period
        company = now.content

        company_sheet = unit_chef.chop_multi(book=book, unit=company)

        if bb_settings.MAKE_ANNUAL_SUMMARIES:
            self._add_annual_summary(book, model)

        unit_chef.chop_multi_valuation(book=book, unit=company, index=1,
                                       recur=False)

        timeline = book.get_sheet_by_name("Timeline")
        timeline.sheet_state = timeline.SHEETSTATE_HIDDEN

        spacer_idx = book.get_index(timeline)
        spacer_sheet = book.create_sheet("Monthly >>", spacer_idx+1)
        spacer_sheet.sheet_properties.tabColor = chef_settings.COVER_TAB_COLOR
        sheet_style.style_sheet(spacer_sheet)

        self._format_line_borders(book)

        return book

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _add_annual_summary(self, book, model):
        """


        ModelChef._add_annual_summary -> None

        --``model`` is an instance of Blackbird Engine model

        Adds an annual summary tab.
        """
        # Create summary tab
        tab_idx = 1
        sheet = book.create_sheet(chef_settings.SUMMARY_TITLE, tab_idx)

        # 2x1 top left corner for company name
        header_rows = sheet.bb.row_axis.add_group('tab_header', size=2)
        header_cols = sheet.bb.col_axis.add_group('tab_header', size=1)

        # Add company name, top left of header section
        address = header_rows.get_corner_address(header_cols)
        cell = sheet.cell(address)
        cell.value = model.time_line.current_period.content.name.title()
        cell.alignment = Alignment(horizontal='left', vertical='center')
        cell.font = Font(size=14, bold=True, underline='single')

        # Output area, size to be calculated
        output_rows = sheet.bb.row_axis.add_group('output_rows')
        output_cols = sheet.bb.col_axis.add_group('output_cols')

        # Output column layout
        # blank column on the left
        colspacer_tip = output_cols.add_group('spacer_tip', size=1)
        # columns for row labels
        label_cols = output_cols.add_group('labels', size=5)
        # columns for years and quarters, size to be calculated
        years_cols = output_cols.add_group('years')
        # blank column at the end
        colspacer_end = output_cols.add_group('spacer_end', size=1)

        # Annual and quarterly column headers, from quarterly summary
        key = model.time_line.summary_builder.QUARTERLY_KEY
        qtr_timeline = model.time_line.summary_builder.summaries[key]
        # calculate the column layout for quarters and years
        self._annual_summary_headers(
            sheet, qtr_timeline, output_rows, output_cols
        )

        # Add parameters area to set up label and value columns
        area = sheet.bb.add_area(field_names.PARAMETERS)
        area.columns.by_name[field_names.LABELS] = label_cols.number()
        area.columns.by_name[field_names.VALUES] = years_cols.number()

        # Add row and label for Complete T/F
        complete_label_rows = output_rows.add_group(
            'complete_label',
            size=1,
            offset=1
        )
        address = complete_label_rows.get_corner_address(label_cols)
        cell = sheet.cell(address)
        cell.value = chef_settings.COMPLETE_LABEL
        cell.alignment = Alignment(horizontal='left', vertical='center')

        # Add row and label for Available Months
        available_months_rows = output_rows.add_group(
            'available_months',
            size=1,
            offset=0
        )
        address = available_months_rows.get_corner_address(label_cols)
        cell = sheet.cell(address)
        cell.value = chef_settings.AVAILABLE_LABEL
        cell.alignment = Alignment(horizontal='left', vertical='center')

        # Fill output: quarterly summary timeline
        if chef_settings.SUMMARY_INCLUDES_QUARTERS:
            # column selector: date -> years_cols.2017.quarters.1Q17
            col_selector = lambda date: years_cols.get_group(
                date.year, 'quarters', self._quarter_name(date)
            )
            # chop quarterly
            self._annual_summary_detail(
                sheet,
                qtr_timeline,
                output_rows,
                output_cols,
                col_selector=col_selector
            )

        # Fill output: annual summary timeline
        key = model.time_line.summary_builder.ANNUAL_KEY
        sum_timeline = model.time_line.summary_builder.summaries[key]
        # column selector: date -> years_cols.2017.year
        col_selector = lambda date: years_cols.get_group(
            date.year, 'year'
        )
        self._annual_summary_detail(
            sheet,
            sum_timeline,
            output_rows,
            output_cols,
            col_selector=col_selector
        )

        # Styling and formatting that's left
        sheet_style.style_sheet(sheet, label_areas=False)

        # Make pretty border
        output_rows.add_group('spacer_end', size=1)
        output_rows.calc_size()
        cell_styles.format_border_group(
            sheet=sheet,
            st_col=output_cols.number(),
            ed_col=output_cols.number() + output_cols.size - 1,
            st_row=output_rows.number(),
            ed_row=output_rows.number() + output_rows.size - 1,
            border_style='thin'
        )

        # Label financial statements
        statement_rowgroup = output_rows.get_group('statements')
        for statement_rows in statement_rowgroup.groups:
            # get title from title row
            header = statement_rows.get_group('title')
            # the actual title is carried in the extra 'title' parameter
            label = header.extra['title']
            row = header.number()
            col = label_cols.number()
            cell_styles.format_area_label(sheet, label, row, col_num=col)

        # Spacer column width, 2 cols on left and right of output
        for spacer in (colspacer_tip, colspacer_end):
            letter = get_column_letter(spacer.number())
            column = sheet.column_dimensions[letter]
            column.width = 4

        sheet.sheet_properties.tabColor = chef_settings.SUMMARY_TAB_COLOR

    def _quarter_name(self, date):
        """


        ModelChef._quarter_name() -> str

        Convenience: datetime.date -> '1Q17'.
        """
        return '{}Q{:02d}'.format(date.month // 3, date.year % 100)

    def _annual_summary_headers(
        self, sheet, timeline, output_rows, output_cols
    ):
        """


        ModelChef._annual_summary_headers() -> None

        --``timeline`` quarterly summary timeline

        Create the layout for column headers the annual summary sheet.
        Fills in year and quarter labels in headers.
        """
        # column group for years
        years_cols = output_cols.get_group('years')
        # row for years headers
        year_headrow = output_rows.add_group('years', offset=1, size=1)
        if chef_settings.SUMMARY_INCLUDES_QUARTERS:
            # row for quarter headers, if needed
            qtr_headrow = output_rows.add_group('quarters', size=1)

        # actual header labels, years and (possibly) quarters
        # nested in the form: years.2017.quarters.1Q17, years.2017.year
        for date in sorted(timeline.keys()):
            # label for year column
            year_name = format(date.year)
            # container for quarters (if requested) and year
            year_colgroup = years_cols.add_group(year_name)
            if chef_settings.SUMMARY_INCLUDES_QUARTERS:
                # label for quarter column
                qtr_name = self._quarter_name(date)
                # sub-container for quarters
                qtr_colgroup = year_colgroup.add_group('quarters')
                # teminal leaf, holds the quarterly values
                qtr_colgroup.add_group(qtr_name, size=1, add_outline=True)
            # column for year itself, after quarters
            year_colgroup.add_group('year', size=1)
        # column layout is known at this point
        output_cols.calc_size()

        # fill out the headers, now that the column positions are known
        for year_colgroup in years_cols.groups:
            # if 'quarters' was set, format quarters column headings
            # quarters show up one row below year_header
            for qtr_col in year_colgroup.get_subgroups('quarters'):
                address = qtr_headrow.get_corner_address(qtr_col)
                cell = sheet.cell(address)
                cell.value = qtr_col.name
                cell_styles.format_subheader_label(cell, alignment='right')
                column = sheet.column_dimensions[cell.column]
                column.width = chef_settings.COLUMN_WIDTH
                column.outline_level = qtr_col.outline
            year_col = year_colgroup.get_group('year')
            # width of the column holding annual numbers
            address = year_headrow.get_corner_address(year_col)
            cell = sheet.cell(address)
            column = sheet.column_dimensions[cell.column]
            column.width = chef_settings.COLUMN_WIDTH
            # year label
            address = year_headrow.get_corner_address(year_colgroup)
            cell = sheet.cell(address)
            cell.value = year_colgroup.name
            cell_styles.format_header_label(cell, alignment='right')
            # merge year header cell if there are quarters
            if year_colgroup.size > 1:
                stretch = year_headrow.get_corner_address(year_col)
                sheet.merge_cells('{}:{}'.format(address, stretch))

    def _annual_summary_detail(self,
        sheet, timeline, output_rows, output_cols, col_selector
    ):
        """


        ModelChef._annual_summary_detail() -> None

        Fills in the periodic data on the annual summary sheet. Period is
        specified by ``col_selector``, which finds the matching output column
        in column headers, and needs to match the ``timeline``.
        """
        complete_label_rows = output_rows.get_group('complete_label')
        available_months_rows = output_rows.get_group('available_months')

        set_labels = True
        for date in timeline.keys():
            column = col_selector(date)

            summary = timeline.find_period(date)
            unit = summary.content
            unit.xl.set_sheet(sheet)
            sheet.bb.outline_level = 0

            # Complete T/F
            address = complete_label_rows.get_corner_address(column)
            cell = sheet.cell(address)
            cell.value = unit.complete
            cell.alignment = Alignment(horizontal='right', vertical='center')

            # Available months
            address = available_months_rows.get_corner_address(column)
            cell = sheet.cell(address)
            cell.value = unit.periods_used
            cell.alignment = Alignment(horizontal='right', vertical='center')

            # Statements
            statement_rowgroup = output_rows.add_group('statements', offset=1)
            for statement in unit.financials.ordered:
                if statement is not None:
                    if statement is unit.financials.ending:
                        line_chef.chop_summary_statement(
                            sheet=sheet,
                            statement=unit.financials.starting,
                            column=column.number(),
                            row_container=statement_rowgroup,
                            set_labels=set_labels,
                            title='starting balance sheet',
                        )
                    line_chef.chop_summary_statement(
                        sheet=sheet,
                        statement=statement,
                        column=column.number(),
                        row_container=statement_rowgroup,
                        set_labels=set_labels,
                    )

    def _build_foundation(self, model):
        """


        ModelChef._build_foundation() -> BB_Workbook


        Return a workbook with:
           cover [not implemented yet]
           scenarios
           timeline
        """
        book = Workbook()


        self._create_cover_tab(book, model)
        self._create_scenarios_tab(book, model)
        self._create_time_line_tab(book, model)

        return book

    def _create_cover_tab(self, book, model):
        """


        ModelChef._create_cover_tab() -> None

        --``book`` is an instance of B_Workbook
        --``model`` is a Blackbird Engine model

        Method adds a cover tab to the workbook
        """
        company = model.time_line.current_period.content

        sheet = book.active
        sheet.title = chef_settings.COVER_TITLE
        sheet_style.style_sheet(sheet, label_areas=False)

        row = sheet.row_dimensions[1]
        row.height = 9

        for r in range(8, 23):
            row = sheet.row_dimensions[r]
            row.height = 21.75

        row = sheet.row_dimensions[18]
        row.height = 9

        column = sheet.column_dimensions['A']
        column.width = 10.71

        column = sheet.column_dimensions['D']
        column.width = 14

        column = sheet.column_dimensions['E']
        column.width = 31.71

        column = sheet.column_dimensions['F']
        column.width = 14

        if chef_settings.INCLUDE_LOGO:
            img = xlio.drawing.image.Image(IMAGE_PATH,
                                           size=(250, None))
            img.anchor(sheet.cell('B2'))

            sheet.add_image(img)

        cell_styles.format_border_group(sheet, 2, 8, 9, 22,
                                        border_style='double')

        cell = sheet.cell('E11')
        cell.value = company.name.title()
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.font = Font(size=18, bold=True, underline='single')

        cell = sheet.cell('D14')
        cell.value = chef_settings.DATE_LABEL
        cell.alignment = Alignment(horizontal='left')
        cell.font = Font(size=12, bold=True)

        cell = sheet.cell('D15')
        cell.value = chef_settings.QCOUNT_LABEL
        cell.alignment = Alignment(horizontal='left')
        cell.font = Font(size=12, bold=True)

        cell = sheet.cell('F14')
        cell.value = model.time_line.current_period.end
        cell.alignment = Alignment(horizontal='right')
        cell.font = Font(size=12)

        # get length of interview
        questions = []
        for i in model.transcript:
            q = i[0]['q_in']
            if q:
                questions.append(q['prompt'])

        cell = sheet.cell('F15')
        cell.value = len(questions)
        cell.alignment = Alignment(horizontal='right')
        cell.font = Font(size=12)

        cell = sheet.cell('C17')
        cell.value = chef_settings.ESTIMATED_LABEL
        cell.font = Font(color=WHITE, size=11, bold=True)
        cell.fill = PatternFill(start_color=BLACK,
                                end_color=BLACK,
                                fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        sheet.merge_cells('C17:G17')

        cell = sheet.cell('C19')
        cell.value = chef_settings.DISCLAIMER_TEXT
        cell.font = Font(size=10)
        cell.alignment = Alignment(horizontal='center', vertical='center',
                                   wrap_text=True)
        sheet.merge_cells('C19:G21')

        sheet.sheet_properties.tabColor = chef_settings.COVER_TAB_COLOR

    def _create_scenarios_tab(self, book, model):
        """


        ModelChef._create_scenarios_tab() -> BB_Worksheet


        Return a worksheet that lays out the assumptions used by the model in
        various scenarios.
        """
        my_tab = book.create_sheet(tab_names.SCENARIOS)

        # Sheet map:
        # A          |  B      | C             | D     | E
        # param names|  blank  | active values | blank | blackbird values

        starting_row = 3

        label_column = 2
        in_effect_column = 4
        custom_column = 6
        base_case_column = 8

        sheet_style.set_column_width(my_tab, in_effect_column)
        sheet_style.set_column_width(my_tab, base_case_column)

        area = my_tab.bb.add_area(field_names.PARAMETERS)

        area.columns.by_name[field_names.LABELS] = label_column
        area.columns.by_name[field_names.VALUES] = in_effect_column
        area.columns.by_name[field_names.CUSTOM_CASE] = custom_column
        area.columns.by_name[field_names.BASE_CASE] = base_case_column

        current_row = starting_row

        area.rows.by_name[field_names.ACTIVE_SCENARIO] = current_row

        book.set_scenario_names(model)
        scenario_columns = book.scenario_names[1:]

        add_scenario_selector(my_tab, label_column, current_row,
                              book.scenario_names)
        selector_cell = my_tab.cell(row=current_row, column=in_effect_column)

        # Make scenario label cells
        custom_cell = my_tab.cell(column=custom_column, row=current_row)
        custom_cell.value = field_names.CUSTOM
        cell_styles.format_scenario_label(custom_cell)

        for i, s in enumerate(scenario_columns):
            scen_cell = my_tab.cell(column=base_case_column+i, row=current_row)
            scen_cell.value = s.title()
            cell_styles.format_scenario_label(scen_cell)
            if i > 0:
                # add columns for other cases to area
                area.columns.by_name[s.lower()+"_case"] = base_case_column+i

        title_row = current_row

        # insert blank row
        current_row += 2

        # storing scenario values in model.time_line is obsolete now, transfer
        # existing values to model.scenarios
        base = model.time_line.parameters
        ref_row = 3

        all_scenarios = dict()
        all_scenarios[field_names.BASE] = base
        all_scenarios.update(model.scenarios)

        for param_name in sorted(base.keys()):
            # Sort to make sure we display the parameters in stable order,
            # otherwise order could vary from chop to chop on the same model.

            label_cell = my_tab.cell(column=label_column, row=current_row)
            label_cell.value = param_name

            area.rows.by_name[param_name] = current_row

            case_cell = my_tab.cell(column=custom_column,
                                    row=current_row)
            case_cell.value = base[param_name]
            cell_styles.format_hardcoded(case_cell)
            cell_styles.format_parameter(case_cell)

            # Loop through scenarios and add values
            for i, s in enumerate(scenario_columns):
                case_cell = my_tab.cell(column=base_case_column+i,
                                        row=current_row)
                case_cell.value = all_scenarios[s].get(param_name, '')
                cell_styles.format_parameter(case_cell)

            start_cos = custom_cell.coordinate
            end_cos = case_cell.coordinate

            link_template = formula_templates.HLOOKUP
            link = link_template.format(ref_coords=selector_cell.coordinate,
                                        start_coords=start_cos,
                                        end_coords=end_cos,
                                        ref_row=ref_row)

            in_effect_cell = my_tab.cell(column=in_effect_column,
                                         row=current_row)
            in_effect_cell.set_explicit_value(link, data_type=type_codes.FORMULA)
            cell_styles.format_parameter(in_effect_cell)

            current_row += 1
            ref_row += 1

        # Add cell outline formatting for Scenarios cells here
        cell_styles.format_border_group(my_tab,
                                             custom_column,
                                             custom_column,
                                             title_row,
                                             current_row-1)

        cell_styles.format_border_group(my_tab,
                                             base_case_column,
                                             base_case_column+i,
                                             title_row,
                                             current_row-1)

        for c in range(1, area.columns.ending+1):
            sheet_style.set_column_width(my_tab, c)

        sheet_style.style_sheet(my_tab)

        my_tab.sheet_properties.tabColor = chef_settings.SCENARIO_TAB_COLOR

        return my_tab

    @staticmethod
    def _create_time_line_tab(book, model):
        """


        ModelChef._create_time_line_tab() -> BB_Worksheet


        Add a sheet that spreads out the time periods and shows each period's
        parameters.

        By default, each period inherits all parameters from the active
        scenario (on the scenarios sheet) by default. If a period specifies its
        own value for a parameter, routine will overwrite the link with a
        hard-coded value.

        Method expects book to include a completed scenarios sheet.
        """
        scenarios = book[tab_names.SCENARIOS]
        scenarios_area = scenarios.bb.parameters

        my_tab = book.create_sheet(tab_names.TIME_LINE)

        parameters = my_tab.bb.add_area(field_names.PARAMETERS)
        time_line = my_tab.bb.add_area(field_names.TIMELINE)

        # Pick starting positions
        local_labels_column = 2
        local_master_column = 4
        sheet_style.set_column_width(my_tab, local_master_column)

        alpha_master_column = get_column_letter(local_master_column)

        parameters.columns.by_name[field_names.LABELS] = local_labels_column
        parameters.columns.by_name[field_names.MASTER] = local_master_column

        header_row = 3
        time_line.rows.by_name[field_names.LABELS] = header_row
        my_tab.bb.current_row = header_row

        # First, pull the parameter names and active values from the scenarios
        # tab into a local "label" and "master" column, respectively.
        external_coordinates = dict()
        external_coordinates["sheet"] = scenarios.title

        source_label_column = scenarios_area.columns.\
            get_position(field_names.LABELS)
        source_value_column = scenarios_area.columns.\
            get_position(field_names.VALUES)

        for param_name in scenarios_area.rows.by_name:
            # We can build the page in any order here

            row_number = scenarios_area.rows.get_position(param_name)
            # Get the correct relative position

            source_coordinates = external_coordinates.copy()
            source_coordinates["row"] = row_number

            active_row = header_row + row_number
            my_tab.bb.parameters.rows.by_name[param_name] = active_row
            # TO DO: Think about whether we should be keeping track of the row
            # number differently here.

            # Label cell should link to the parameter name on the scenarios
            # sheet
            label_cell = my_tab.cell(column=local_labels_column,
                                     row=active_row)

            cos = source_coordinates.copy()
            cos["alpha_column"] = get_column_letter(source_label_column)

            link = formula_templates.ADD_CELL_FROM_SHEET.format(**cos)
            label_cell.set_explicit_value(link, data_type=type_codes.FORMULA)

            # Master cell should link to the active value
            master_cell = my_tab.cell(column=local_master_column,
                                      row=active_row)

            cos = source_coordinates.copy()
            cos["alpha_column"] = get_column_letter(source_value_column)
            link = formula_templates.ADD_CELL_FROM_SHEET.format(**cos)
            master_cell.set_explicit_value(link, data_type=type_codes.FORMULA)
            cell_styles.format_parameter(master_cell)

        my_tab.bb.current_row = active_row
        # Second, build a column for each period. Pull values from our local
        # master column and overwrite them if necessary with direct values.

        starting_column = local_master_column + 2
        active_column = starting_column

        past, present, future = model.time_line.get_segments()
        covered_dates = present + future
        for end_date in covered_dates:

            period = model.time_line[end_date]

            my_tab.bb.time_line.columns.by_name[period.end] = active_column
            parameters.columns.by_name[period.end] = active_column

            sheet_style.set_column_width(my_tab, active_column)
            # Need this to make sure the parameters Area looks as wide as the
            # timeline. Otherwise, other routines may think that the params
            # area is only one column wide.

            header_cell = my_tab.cell(column=active_column, row=header_row)
            header_cell.value = period.end
            cell_styles.format_date(header_cell)

            # 1. Pulling the master values for each parameter.
            # my_tab.bb.current_row += 2
            existing_params = dict()
            for k in my_tab.bb.parameters.rows.by_name:
                # May write the column in undefined order
                param_row = my_tab.bb.parameters.rows.by_name[k]

                param_cell = my_tab.cell(column=active_column, row=param_row)
                cell_styles.format_parameter(param_cell)

                link_template = formula_templates.ADD_CELL

                cos = dict(alpha_column=alpha_master_column, row=param_row)
                link = link_template.format(**cos)

                param_cell.set_explicit_value(link,
                                              data_type=type_codes.FORMULA)
                cell_styles.format_parameter(param_cell)

                existing_params[k] = link

            # 2. Overwrite links with hard-coded values where the period
            #    specifies them. Add period-specific parameters.

            existing_param_names = period.parameters.keys() & \
                                   parameters.rows.by_name.keys()
            new_param_names = period.parameters.keys() - existing_param_names

            # New parameters are specific to the period. We don't have a row
            # for them on the sheet yet, so we'll add them later.

            for spec_name in existing_param_names:
                spec_value = period.parameters[spec_name]

                param_row = parameters.rows.get_position(spec_name)
                m_cell = my_tab.cell(column=local_master_column,
                                     row=param_row)

                param_cell = my_tab.cell(column=active_column, row=param_row)
                if spec_value != m_cell.value:
                    param_cell.value = spec_value
                    cell_styles.format_hardcoded(param_cell)
                else:
                    cos = dict(alpha_column=alpha_master_column, row=param_row)
                    link = link_template.format(**cos)
                    param_cell.set_explicit_value(link,
                                                  data_type=type_codes.FORMULA)

                cell_styles.format_parameter(param_cell)

            new_params = dict()
            for k in new_param_names:
                new_params[k] = period.parameters[k]

            my_tab.bb.current_row = parameters.rows.ending
            unit_chef.add_items_to_area(
                sheet=my_tab,
                area=my_tab.bb.parameters,
                items=new_params,
                active_column=active_column,
                format_func=cell_styles.format_parameter
                )

            # Upgrade-S: For speed, can supply master and label column indices
            # to the add_items() routine.

            active_column += 1

        # Freeze panes:
        corner_row = my_tab.bb.time_line.rows.ending
        corner_row += 1

        corner_column = my_tab.bb.parameters.columns.get_position(field_names.MASTER)
        corner_column += 1

        corner_cell = my_tab.cell(column=corner_column, row=corner_row)
        my_tab.freeze_panes = corner_cell

        # Add selection cell
        if SCENARIO_SELECTORS:
            selector_row = my_tab.bb.parameters.rows.by_name[field_names.ACTIVE_SCENARIO]
            add_scenario_selector(my_tab, local_labels_column, selector_row,
                                  book.scenario_names)

        sheet_style.style_sheet(my_tab)

        my_tab.sheet_properties.tabColor = chef_settings.TIMELINE_TAB_COLOR

        return my_tab

    @staticmethod
    def _format_line_borders(book):
        """


        model_chef._format_line_borders() -> None

        --``book`` is the workbook to format

        Function manipulates workbook in place, adding borders to rows where
        line items request them.
        """
        for sheet in book.worksheets:

            if not getattr(sheet, 'bb', None):
                continue

            if not sheet.bb.line_directory:
                continue

            # go through all lines in sheet.bb.line_directory and add border
            # formatting, if any
            st_col = sheet.bb.parameters.columns.by_name[field_names.VALUES]
            if 'time_line' in sheet.bb.area_names:
                ed_col = min((sheet.bb.time_line.columns.ending,
                              sheet.max_column))
            else:
                ed_col = sheet.max_column - 1

            for xl in sheet.bb.line_directory.values():
                row = xl.cell.row
                border = xl.format.border

                if not border:
                    continue

                cell_styles.format_border_group(sheet, st_col=st_col,
                                                ed_col=ed_col, st_row=row,
                                                ed_row=row, border_style=border)
