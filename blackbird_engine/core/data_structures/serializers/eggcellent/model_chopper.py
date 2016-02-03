#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.serializers.eggcellent.model_chopper
"""

Module defines workbook with custom native-Python data storage on each sheet.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ModelChopper          chop Blackbird Engine model into a dynamic Excel workbook
====================  ==========================================================
"""




# Imports
from .bb_workbook import BB_Workbook as Workbook
from .tab_names import TabNames




# Constants
# n/a

# Module Globals
# n/a

# Classes
class ModelChopper:
    """

    Class packages an Engine model into an Excel Workbook with dynamic links.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    tab_names             standard tab names

    FUNCTIONS:
    chop_model()          returns sheet with a SheetData instance at sheet.bb
    ====================  ======================================================
    """
    tab_names = TabNames()
    
    
    def chop_model(self, model):
        """

        -> Workbook

        """
        # self._import_historical_data(model)
        
        book = self._spread_foundation(model)
        now = model.time_line.current_period
        company = now.content
        
        UnitChopper.chop_unit(company, book)
        # <-------------------------------------------------------------------------------- May need to specify period, column, etc.

        # book = self._create_annual_summary_tab(model, book)
        # book = self._create_dcf_tab(model, book)
        # book = self._create_ev_tab(model, book)
                
        return book

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _spread_foundation(self, model):
        """

        -> book
        
        Return a workbook with:
           cover [not implemented yet]
           scenarios
           timeline
           
        """       
        book = Workbook()
        
        # self._create_cover_tab(model, book)
        self._create_scenarios_tab(book)
        self._create_time_line_tab(book)

        return book

    def _create_scenarios_tab(self, book, model):
        """

        -> should return sheet

        """
        scenarios = book.create_sheet(self.tab_names.SCENARIOS)

        # Sheet map:
        # A          |  B      | C             | D     | E
        # param names|  blank  | active values | blank | blackbird values

        starting_row = 1
        starting_column = 1
        # should make this a lookup table too: column name to index
        
        scenarios.bb.general.columns.by_name["params"] = 1
        scenarios.bb.general.columns.by_name["active"] = 3
        scenarios.bb.general.columns.by_name["base"] = 5
        # these keys should be standard
        # all other scenarios should be a function of selection
        # can do something like bb_case cells are an index of bb scenarios
        # and then active just points to those

        active_row = starting_row

        f_pull_from_cell = "=%s"
        
        for param_name in sorted(model.time_line.parameters):
            # Use sorted to make sure order is consistent

            label_cell = scenarios.cell(row=active_row, column=starting_column)
            scenarios.bb.general.rows.by_name[param_name] = active_row

            active_cell = scenarios.cell(row=active_row, column=(starting_column+2)) #<--------------------------------fix the column indexing
            bb_cell = scenarios.cell(row=active_row, column=(starting_column+4))
            # ideally should be active_cell.column+2 <---------------------------------------------------------------- fix the coordinates
                        
            label_cell.value = param_name
            bb_cell.value = model.time_line.parameters[param_name]

            active_cell.value = f_pull_from_cell % bb_cell.coordinate

            active_row += 1
            
        #Can expand this logic to print every scenario
        
        return scenarios

    def _create_time_line_tab(self, book, model):
        """

        -> sheet ?

        book should have a "scenarios" tab by now
        """
        
        scenarios = book[self.tab_names.SCENARIOS]
        
        my_tab = book.create_sheet(self.tab_names.TIME_LINE)
        my_tab.bb.parameters = Area()

        get_column_letter = excel_interface.utils.get_column_letter

        # first column will be params
        # second column will be blank
        # third column will be master
        
        col_params = 1
        col_master = 3
        # have to record column <--------------------------------------------------------------------------------------------------------------

        header_row = 3
        
        f_active_scenario = "=Scenarios!C%s"
        # first, write the param colum and the master column: "=Scenarios! $A1"

        # Make the param name and master value columns
        for param_name, row_number in scenarios.bb.general.rows.by_name.items(): #<-----------------------------------need to make sure we get the right position here
            # Order doesn't matter here

            active_row = header_row + row_number
            my_tab.bb.parameters.rows.by_name[param_name] = active_row
            #<--------------------------------------------------------------------------------have to think about whether these are absolute or relative
            
            name_cell = my_tab.cell(column=col_params, row=active_row)
            name_cell.value = param_name

            master_cell = my_tab.cell(column=col_master, row=active_row)
            master_cell.value = f_active_scenario % row_number

        f_pull_master = "=" + "$" + get_column_letter(col_master) + "%s"
        # "=$A1"
        
        starting_column = col_master + 2
        active_column = starting_column

        my_tab.bb.time_line.rows.by_name["labels"] = header_row
        
        for period in model.time_line.get_ordered():

            my_tab.bb.time_line.columns.by_name[period.end] = active_column
            my_tab.bb.parameters.columns.by_name[period_end] = active_column
            
            header_cell = my_tab.cell(column=active_column, row=header_row)
            header_cell.value = period.end

            # first, add period-level parameters
            # first, drop the pull value for all cells through the params thing
            for param_row in my_tab.bb.parameters.rows.by_name.values():
                
                # Note: will probably write cells in non-sequential order

                param_cell = my_tab.cell(column=active_column, row=param_row)
                param_cell.value = f_pull_master % param_row

                # Or could add links to the prior period's parameters <--------------------------

            # then, overwrite them with explicitly specified params
            for spec_name, spec_value in period.parameters.items():
                param_row = my_tab.bb_row_lookup[spec_name]
                param_cell = my_tab.cell(column=active_column, row=param_row)
                param_cell.value = spec_value
##                spec_cell.format = blue_font_color
            
            active_column += 1
            # Move on to the next period

        return my_tab
  

        
