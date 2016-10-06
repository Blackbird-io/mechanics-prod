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
import datetime
import os
import openpyxl as xlio
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.styles.colors import WHITE, BLACK

import bb_settings
import chef_settings
from ._chef_tools import add_scenario_selector
from .bb_workbook import BB_Workbook as Workbook
from .cell_styles import CellStyles
from .data_types import TypeCodes
from .field_names import FieldNames
from .formulas import FormulaTemplates
from .line_chef import LineChef
from .sheet_style import SheetStyle
from .tab_names import TabNames
from .transcript_chef import TranscriptChef
from .unit_chef import UnitChef
from .summary_chef import SummaryChef
from .unit_structure import StructureChef




# Constants
IMAGE_PATH = os.path.join(
    os.path.dirname(__file__), 'static', 'blackbird_engine_2X_410x120.png'
)

# Module Globals
cell_styles = CellStyles()
field_names = FieldNames()
formula_templates = FormulaTemplates()
line_chef = LineChef()
sheet_style = SheetStyle()
tab_names = TabNames()
transcript_chef = TranscriptChef()
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

        structure_chef = StructureChef()
        structure_chef.chop(book, company, index=5)

        unit_chef.chop_multi(book=book, unit=company)

        if bb_settings.MAKE_ANNUAL_SUMMARIES:
            summary_chef = SummaryChef()
            summary_chef.add_annual_summary(book, model)

        unit_chef.chop_multi_valuation(book=book, unit=company, index=2,
                                       recur=False)

        temp_sheet = book.get_sheet_by_name(tab_names.SCENARIOS)
        spacer_idx = book.get_index(temp_sheet) + 1
        spacer_sheet = book.create_sheet("Details >>", spacer_idx)
        spacer_sheet.sheet_properties.tabColor = chef_settings.COVER_TAB_COLOR
        sheet_style.style_sheet(spacer_sheet)

        transcript_chef.make_transcript_excel(model, book, idx=3)

        CellStyles.format_line_borders(book)

        return book

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _build_foundation(self, model):
        """


        ModelChef._build_foundation() -> BB_Workbook


        Return a workbook with:
           cover [not implemented yet]
           scenarios
           timeline
        """
        book = Workbook()
        book.properties.creator = chef_settings.WORKBOOK_AUTHOR

        self._create_cover_tab(book, model)
        self._create_scenarios_tab(book, model)

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
        sheet.title = tab_names.COVER
        sheet_style.style_sheet(sheet, label_areas=False)

        row = sheet.row_dimensions[1]
        row.height = 9

        for r in range(8, 24):
            row = sheet.row_dimensions[r]
            row.height = 21.75

        row = sheet.row_dimensions[19]
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

        cell_styles.format_border_group(sheet, 2, 8, 9, 23,
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
        cell.value = chef_settings.REF_DATE_LABEL
        cell.alignment = Alignment(horizontal='left')
        cell.font = Font(size=12, bold=True)

        cell = sheet.cell('D16')
        cell.value = chef_settings.QCOUNT_LABEL
        cell.alignment = Alignment(horizontal='left')
        cell.font = Font(size=12, bold=True)

        cell = sheet.cell(chef_settings.COVER_DATE_CELL)
        cell.value = datetime.date.today()
        cell.alignment = Alignment(horizontal='right')
        cell.font = Font(size=12)

        cell = sheet.cell('F15')
        cell.value = model.time_line.ref_date
        cell.alignment = Alignment(horizontal='right')
        cell.font = Font(size=12)

        # get length of interview
        questions = []
        for i in model.transcript:
            q = i[0]['q_in']
            if q:
                questions.append(q['prompt'])

        cell = sheet.cell('F16')
        cell.value = len(questions)
        cell.alignment = Alignment(horizontal='right')
        cell.font = Font(size=12)

        cell = sheet.cell('C18')
        cell.value = chef_settings.ESTIMATED_LABEL
        cell.font = Font(color=WHITE, size=11, bold=True)
        cell.fill = PatternFill(start_color=BLACK,
                                end_color=BLACK,
                                fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        sheet.merge_cells('C18:G18')

        cell = sheet.cell('C20')
        cell.value = chef_settings.DISCLAIMER_TEXT
        cell.font = Font(size=10)
        cell.alignment = Alignment(horizontal='center', vertical='center',
                                   wrap_text=True)
        sheet.merge_cells('C20:G22')

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

        starting_row = 2

        label_column = 2
        in_effect_column = 12
        custom_column = 4
        base_case_column = 6

        area = my_tab.bb.add_area(field_names.PARAMETERS)
        timeline = my_tab.bb.add_area(field_names.TIMELINE)

        area.columns.by_name[field_names.LABELS] = label_column
        area.columns.by_name[field_names.VALUES] = in_effect_column
        area.columns.by_name[field_names.CUSTOM_CASE] = custom_column
        area.columns.by_name[field_names.BASE_CASE] = base_case_column

        timeline.columns.by_name[field_names.LABELS] = label_column

        current_row = starting_row

        book.set_scenario_names(model)
        scenario_columns = book.scenario_names[1:]

        add_scenario_selector(my_tab, label_column, current_row,
                              book.scenario_names)
        selector_cell = my_tab.cell(row=current_row, column=custom_column)
        selector_cell.value = field_names.CUSTOM
        my_tab.bb.general.rows.by_name[field_names.SELECTOR] = current_row

        current_row += 3
        # Make scenario label cells
        custom_cell = my_tab.cell(column=custom_column, row=current_row)
        custom_cell.value = field_names.CUSTOM
        cell_styles.format_scenario_label(custom_cell)

        for i, s in enumerate(scenario_columns):
            scen_cell = my_tab.cell(
                column=base_case_column + i, row=current_row
            )
            scen_cell.value = s.title()
            cell_styles.format_scenario_label(scen_cell)
            if i > 0:
                # add columns for other cases to area
                area.columns.by_name[s.lower() + "_case"] = base_case_column + i

        active_label_cell = my_tab.cell(column=in_effect_column,
                                        row=current_row)
        active_label_cell.value = field_names.IN_EFFECT
        cell_styles.format_scenario_label(active_label_cell)

        title_row = current_row

        # insert blank row
        current_row += 2

        # storing scenario values in model.time_line is obsolete now, transfer
        # existing values to model.scenarios
        base = model.time_line.parameters
        base.update(model.time_line.current_period.parameters)

        # now loop through the rest of the time periods and grab parameters
        for per in model.time_line.values():
            if per.end < model.time_line.current_period.end:
                continue

            existing_parms = set(base.keys())
            tp_parms = set(per.parameters.keys())
            new_parms = tp_parms - existing_parms

            for p in new_parms:
                base[p] = None

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
                case_cell = my_tab.cell(column=base_case_column + i,
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
            in_effect_cell.set_explicit_value(
                link, data_type=type_codes.FORMULA
            )
            cell_styles.format_parameter(in_effect_cell)

            current_row += 1
            ref_row += 1

        # Add cell outline formatting for Scenarios cells here
        cell_styles.format_border_group(
            my_tab,
            custom_column,
            custom_column,
            title_row,
            current_row - 1
        )

        cell_styles.format_border_group(
            my_tab,
            base_case_column,
            base_case_column + i,
            title_row,
            current_row - 1
        )

        cell_styles.format_border_group(
            my_tab,
            in_effect_column,
            in_effect_column,
            title_row,
            current_row - 1
        )

        # Now add the timeline area
        active_column = in_effect_column + 2
        tl_start = active_column
        alpha_master_column = get_column_letter(in_effect_column)

        past, present, future = model.time_line.get_segments()
        covered_dates = present + future
        for end_date in covered_dates:
            period = model.time_line[end_date]

            timeline.columns.by_name[period.end] = active_column

            sheet_style.set_column_width(my_tab, active_column)
            # Need this to make sure the parameters Area looks as wide as the
            # timeline. Otherwise, other routines may think that the params
            # area is only one column wide.

            header_cell = my_tab.cell(column=active_column, row=title_row)
            header_cell.value = period.end
            cell_styles.format_date(header_cell)
            col = chef_settings.TIMELINE_HEADER_COLOR
            cell_styles.format_header_label(header_cell, font_color=WHITE,
                                            color=col, bold=False)

            timeline.rows.by_name = area.rows.by_name.copy()

            for k in timeline.rows.by_name:
                # May write the column in undefined order
                param_row = timeline.rows.by_name[k]
                param_cell = my_tab.cell(column=active_column, row=param_row)

                master_cell = my_tab.cell(
                    column=in_effect_column, row=param_row
                )

                link2master = True
                if k in period.parameters:
                    param_cell.value = period.parameters[k]

                    if param_cell.value != master_cell.value:
                        cell_styles.format_hardcoded(param_cell)
                        link2master = False

                if link2master:
                    link_template = formula_templates.ADD_CELL
                    cos = dict(alpha_column=alpha_master_column, row=param_row)
                    link = link_template.format(**cos)

                    param_cell.set_explicit_value(
                        link, data_type=type_codes.FORMULA
                    )

                cell_styles.format_parameter(param_cell)

            active_column += 1

        tl_end = active_column - 1
        timeline.rows.by_name[field_names.TITLE] = title_row

        for col in range(tl_start, tl_end + 1):
            alpha = get_column_letter(col)
            my_tab.column_dimensions[alpha].outline_level = 1

        for col in range(base_case_column, in_effect_column + 1):
            alpha = get_column_letter(col)
            my_tab.column_dimensions[alpha].outline_level = 1

        for c in range(1, area.columns.ending + 1):
            sheet_style.set_column_width(my_tab, c)

        sheet_style.set_column_width(my_tab, custom_column + 1, 12)
        sheet_style.set_column_width(my_tab, in_effect_column + 1, 12)
        sheet_style.set_column_width(my_tab, in_effect_column - 1, 12)

        corner_col = area.columns.by_name[field_names.BASE_CASE]
        corner_row = title_row + 1
        corner_cell = my_tab.cell(column=corner_col, row=corner_row)
        my_tab.freeze_panes = corner_cell

        sheet_style.style_sheet(my_tab, label_areas=False)
        my_tab.sheet_properties.tabColor = chef_settings.SCENARIO_TAB_COLOR

        return my_tab
