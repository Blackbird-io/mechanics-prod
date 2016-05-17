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
import openpyxl as xlio

from .bb_workbook import BB_Workbook as Workbook

from ._chef_tools import add_scenario_selector
from .cell_styles import CellStyles
from .chef_settings import SCENARIO_SELECTORS
from .data_types import TypeCodes
from .field_names import FieldNames
from .formulas import FormulaTemplates
from .sheet_style import SheetStyle
from .tab_names import TabNames
from .unit_chef import UnitChef




# Constants
# n/a

# Module Globals
cell_styles = CellStyles()
field_names = FieldNames()
formula_templates = FormulaTemplates()
sheet_style = SheetStyle()
tab_names = TabNames()
type_codes = TypeCodes()
unit_chef = UnitChef()

get_column_letter = xlio.utils.get_column_letter

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

        return book

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _build_foundation(self, model):
        """


        ModelChef._build_foundation() -> BB_Workbook
        

        Return a workbook with:
           cover [not implemented yet]
           scenarios
           timeline
        """       
        book = Workbook()
        
        # self._create_cover_tab(book, model)
        self._create_scenarios_tab(book, model)
        self._create_time_line_tab(book, model)

        return book

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
        cell_styles.format_thin_border_group(my_tab,
                                             custom_column,
                                             custom_column,
                                             title_row,
                                             current_row-1)

        cell_styles.format_thin_border_group(my_tab,
                                             base_case_column,
                                             base_case_column+i,
                                             title_row,
                                             current_row-1)

        for c in range(1, area.columns.ending+1):
            sheet_style.set_column_width(my_tab, c)

        sheet_style.style_sheet(my_tab)

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
            for k in my_tab.bb.parameters.rows.by_name.keys():
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
                param_cell = my_tab.cell(column=active_column, row=param_row)
                param_cell.value = spec_value
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

        # Add selection cell
        if SCENARIO_SELECTORS:
            selector_row = my_tab.bb.parameters.rows.by_name[field_names.ACTIVE_SCENARIO]
            add_scenario_selector(my_tab, local_labels_column, selector_row,
                                  book.scenario_names)

        sheet_style.style_sheet(my_tab)

        return my_tab
