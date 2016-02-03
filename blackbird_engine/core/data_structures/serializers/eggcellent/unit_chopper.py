#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.serializers.eggcellent.unit_chopper
"""

Module defines a class that represents arbitrarily rich BusinessUnit instances
as a collection of linked Excel worksheets. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
UnitChopper           chop BusinessUnit into dynamic Excel structure
====================  ==========================================================
"""




# Imports
# n/a



# Constants
# n/a

# Module Globals
# n/a

# Classes
class UnitChopper:
    """

    Class packages an Engine model into an Excel Workbook with dynamic links.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    field_names
    formula_templates
    tab_names             standard tab names

    FUNCTIONS:
    chop_model()          returns sheet with a SheetData instance at sheet.bb
    ====================  ======================================================
    """
 
    def chop_unit(self, book, unit):
        """

        -> sheet

        Children should be spread before parent
        """
        children = unit.components.get_ordered()

        for child in children:
            
            self.chop_unit(book, child)

        sheet = self._create_unit_sheet(unit)
        unit.xl.set_sheet(sheet)

        self._add_params(sheet, unit)
##        self._add_life(sheet, unit)
        self._add_financials(sheet, unit)

        return sheet

        # Premise 1: by the time you run this routine, all children should already be in book
        # Premise 2: a unit without any children should be easy to spread on a sheet
        # Premise 3:

    def _add_financials(self, sheet, unit):
        unit.fill_out()
        # fill out populates the unit with all of the information
        
        for statement in unit.financials:
            for line in statement.get_ordered():

                self._spread_line(sheet, line)

    # Have to manage book depth (ie max sheets) #<--------------------------------------------------!!
    
    def _add_unit_params(self, sheet, unit):
        """

        -> sheet
        
        """

        period_column = sheet.bb.time_line.columns.get_position(unit.period.ends)
        label_column = sheet.bb.parameters.columns.get_position("label")
        
        for param_name in sorted(unit.parameters):

            param_value = unit.parameters[param_name]

            if param_name in sheet.bb.parameters.rows.by_name:

                existing_row = sheet.bb.parameters.rows.get_position(param_name)
                data_cell = sheet.cell(column=period_column, row=existing_row)
                data_cell.value = param_value
                # should format the cell in blue or whatever for hardcoded

            else:

                new_row = sheet.bb.parameters.ending + 1
                data_cell = sheet.cell(column=period_column, row=new_row)
                data_cell.value = param_value

                label_cell = sheet.cell(column=label_column, row=new_row)
                label_cell.value = param_name

        return sheet

    def _create_unit_sheet(self, book, unit):

        name = str(unit.id.bbid)[-8:] #<-----------------------------------------------------------------should be a class var
        sheet = book.create_sheet(name)
        unit.xl.set_sheet(sheet)

        self._link_to_time_line(sheet, book)
        self._add_unit_params(sheet, unit)

        return sheet   

    def _link_to_area(self, source_sheet, local_sheet, area_name):
        """
        """

        source_area = getattr(source.bb, area_name)
        local_area = getattr(local.bb, area_name, None)
        if local_area is None:
            local_area = Area()
            setattr(local.bb, range_name, local_area)

        local_area.update(source_area)
        
        coordinates = {
            "sheet" : source_sheet.name
            }
        
        for row in source_area.rows.by_name.values():

            source_row = source_area.rows.starting + row
            local_row = local_area.rows.starting + row

            for column in source_area.columns.by_name.values():

                source_col = source_area.columns.starting + column
                local_col = source_area.columns.starting + column

                local_cell = local_sheet.cell(column=local_column, row=local_row)

                cos = coordinates.copy()
                cos["row"] = source_row
                cos["column"] = source_column

                link = self.formulas.ADD_FOREIGN_CELL.format(**cos)
                local_cell.value = link
                
        # if group, group starting and ending
        return local_sheet

    def _link_to_time_line(self, book, sheet):
        """

        -> sheet

        Link sheet to book's time_line
        """
        source = book[self.names.TIME_LINE]
        
        self._link_to_area(source, sheet, "time_line")
        self._link_to_area(source, sheet, "parameters")

    
