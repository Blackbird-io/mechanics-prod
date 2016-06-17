# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.line_chef
"""

Module defines LineChef class which converts Statement and LineItem objects
into dynamic Excel format.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LineChef              class with methods to chop BB statements into dynamic
                      Excel structures
====================  =========================================================
"""




# Imports
import re

import openpyxl as xlio
from openpyxl.comments import Comment

from data_structures.modelling.line_item import LineItem

from ._chef_tools import group_lines
from .cell_styles import CellStyles
from .chef_settings import COMMENT_FORMULA_NAME, COMMENT_FORMULA_STRING, \
                           COMMENT_CUSTOM, BLANK_BETWEEN_TOP_LINES
from .data_types import TypeCodes
from .field_names import FieldNames
from .formulas import FormulaTemplates

from bb_exceptions import ExcelPrepError



# Constants
# n/a

# Module Globals
cell_styles = CellStyles()
field_names = FieldNames()
formula_templates = FormulaTemplates()
type_codes = TypeCodes()

get_column_letter = xlio.utils.get_column_letter

# Classes
class LineChef:
    """

    Class packages Statement and LineItem objects into dynamic Excel workbook.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    chop_line()           returns Worksheet containing LineItem instances
                          converted to dynamic Excel links
    chop_statement()      returns Worksheet containing Statement instances
                          converted to dynamic Excel links
    ====================  =====================================================
    """

    def chop_line(self, *pargs, sheet, column, line, set_labels=True, indent=0):
        """


        LineChef.chop_line() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Method walks through LineItems and their details and converts them to
        dynamic links in Excel cells.  Method adds consolidation and derivation
        logic to cells.

        Method relies on sheet.bb.current_row being up-to-date.

        Routines deliver sheet with the current_row pointing to the last filled
        in cell.
        """

        self._add_reference(
            sheet=sheet,
            column=column,
            line=line,
            set_labels=set_labels,
            indent=indent
            )

        self._add_derivation_logic(
            sheet=sheet,
            column=column,
            line=line,
            set_labels=set_labels,
            indent=indent + LineItem.TAB_WIDTH
            )

        self._add_consolidation_logic(
            sheet=sheet,
            column=column,
            line=line,
            set_labels=set_labels,
            indent=indent
            )

        details = line.get_ordered()
        if details:
            sheet.bb.current_row += 1

            # Should have the header here instead
            sheet.bb.outline_level += 1
            self._group_lines(sheet)
            
            sub_indent = indent + LineItem.TAB_WIDTH
            detail_summation = ""

            for detail in details:

                sheet.bb.current_row += 1

                sheet.bb.outline_level += 1
                self._group_lines(sheet)
                sheet.bb.outline_level -= 1

                self.chop_line(
                    sheet=sheet,
                    column=column,
                    line=detail,
                    set_labels=set_labels,
                    indent=sub_indent)

                link_template = formula_templates.ADD_COORDINATES

                cos = detail.xl.get_coordinates()
                link = link_template.format(coordinates=cos)
                detail_summation += link

            else:
                # Should group all the details here
                sheet.bb.current_row += 1

                subtotal_cell = sheet.cell(column=column,
                                           row=sheet.bb.current_row)
                subtotal_cell.set_explicit_value(detail_summation,
                                                 data_type=type_codes.FORMULA)

                line.xl.detailed.ending = sheet.bb.current_row
                line.xl.detailed.cell = subtotal_cell

                self._group_lines(sheet)

                if set_labels:
                    label_column = None
                    if not getattr(sheet.bb, "parameters", None):
                        label_column = 1

                    label = indent*" " + line.tags.name + ": details"
                    self._set_label(sheet=sheet,
                                    label=label,
                                    row=sheet.bb.current_row,
                                    column=label_column)

            sheet.bb.outline_level -= 1

        if not line.xl.reference.source:
            self._combine_segments(
                sheet=sheet,
                column=column,
                line=line,
                set_labels=set_labels,
                indent=indent)

        cell_styles.format_line(line)

        return sheet

    def chop_statement(self, *pargs, sheet, column, statement, set_labels=True):
        """


        LineChef.chop_statement() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``statement`` must be an instance of Statement
        --``set_labels`` must be a boolean; True will set labels for line

        Method walks through Statement lines and delegates LineChef.chop_line()
        to add them as dynamic links in Excel.

        Method relies on sheet.bb.current_row being up-to-date.
        """
        if not BLANK_BETWEEN_TOP_LINES:
            sheet.bb.current_row += 1

        for line in statement.get_ordered():
            if BLANK_BETWEEN_TOP_LINES:
                sheet.bb.current_row += 1

            self.chop_line(
                sheet=sheet,
                column=column,
                line=line,
                set_labels=set_labels)

        if len(statement.get_ordered()) == 0:
            sheet.bb.current_row += 1

        return sheet

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _add_consolidation_logic(self, *pargs, sheet, column, line,
                                 set_labels=True, indent=0):
        """


        LineChef._add_consolidation_logic() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Expects line.xl.consolidated.sources to include full range of pointers
        to source lines on children.

        Always stuffs consolidation into the same number of rows.
        Derive can still cause staircasing if the line picks up details in the
        future that it doesn't have now.

        Returns Worksheet with consolidation logic added as Excel dynamic links
        """

        if not line.xl.consolidated.sources:
            pass

        else:
            sources = line.xl.consolidated.sources.copy()

            required_rows = sheet.bb.consolidation_size
            n_sources = len(sources)
            links_per_cell = n_sources // required_rows
            links_per_cell = max(1, links_per_cell)
            # Make sure we include at least 1 link per cell.

            link_template = formula_templates.ADD_COORDINATES

            sheet.bb.current_row += 1
            sheet.bb.outline_level += 1

            line.xl.consolidated.starting = sheet.bb.current_row

            count = 0
            for rr in range(required_rows):

                if sources:
                    batch_summation = ""
                    if rr == required_rows-1:
                        links_to_use = n_sources-count
                    else:
                        links_to_use = links_per_cell

                    for i in range(links_to_use):

                        if sources:
                            source_line = sources.pop(0)
                            # Can reverse sources for better performance.
                            source_cos = source_line.xl.get_coordinates()
                            link = link_template.format(coordinates=source_cos)
                            batch_summation += link
                            count += 1
                        else:
                            break

                        # Inner loop will only run once if ``sources`` is empty

                    if batch_summation:
                        batch_cell = sheet.cell(column=column,
                                                row=sheet.bb.current_row)
                        batch_cell.set_explicit_value(batch_summation,
                                                      data_type=
                                                      type_codes.FORMULA)

                self._group_lines(sheet)

                # Move on to next row
                line.xl.consolidated.ending = sheet.bb.current_row
                sheet.bb.current_row += 1

            # Group the cells
            alpha_column = get_column_letter(column)
            summation_params = {
                "starting_row" : line.xl.consolidated.starting,
                "ending_row" : line.xl.consolidated.ending,
                "alpha_column" : alpha_column
                }

            summation = formula_templates.SUM_RANGE.format(**summation_params)
            summation_cell = sheet.cell(column=column,
                                        row=sheet.bb.current_row)
            summation_cell.set_explicit_value(summation,
                                              data_type=type_codes.FORMULA)

            line.xl.consolidated.cell = summation_cell

            if set_labels:
                label = line.tags.name + ": consolidated results"
                label = (indent * " ") + label
                self._set_label(sheet=sheet, label=label,
                                row=sheet.bb.current_row)

            line.xl.consolidated.ending = sheet.bb.current_row
            self._group_lines(sheet)

            sheet.bb.outline_level -= 1

        return sheet

    def _add_derivation_logic(self, *pargs, sheet, column, line,
                              set_labels=True, indent=0):
        """

        LineChef._add_derivation_logic() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Delegates to LineChef._add_driver_calculation() to add driver logic
        to dynamic links in Excel cells.
        """

        if not line.xl.derived.calculations:
            pass

        else:

            for data_cluster in line.xl.derived.calculations:

                sheet.bb.current_row += 1
                self._group_lines(sheet)

                self._add_driver_calculation(
                    sheet=sheet,
                    column=column,
                    line=line,
                    driver_data=data_cluster,
                    set_labels=set_labels,
                    indent=indent)

            else:
                pass

                # NOTE: No summation at the end of the derive process. Final
                # derived value may OR MAY NOT be the sum of priors. Up to
                # driver to decide.

        return sheet

    def _add_driver_calculation(self, *pargs, sheet, column, line, driver_data,
                                set_labels=True, indent=0):
        """


        LineChef._add_driver_calculation -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``driver_data`` must be a dictionary of driver_data info
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Writes driver logic to Excel sheet. Will write to sheet.bb.current_row.
        """
        sheet.bb.outline_level += 1

        private_data = sheet.bb.parameters.copy()
        # Set up a private range that's going to include both "shared" period &
        # unit parameters from the column and "private" driver parameters.

        label_column = sheet.bb.parameters.columns.get_position(field_names.LABELS)
        period_column = column

        # get params to keep
        params_keep = []
        for step in driver_data.formula.values():
            temp_step = [m.start() for m in re.finditer('parameters\[*', step)]

            for idx in temp_step:
                jnk = step[idx:]
                idx_end = jnk.find(']')+idx
                params_keep.append(step[idx+11:idx_end])

        # clean driver_data
        new_rows = []
        for item in driver_data.rows:
            if item['labels'] in params_keep:
                new_rows.append(item)

        driver_data.rows = new_rows

        for row_data in sorted(driver_data.rows,
                               key=lambda x: x[field_names.LABELS]):

            private_label = row_data[field_names.LABELS]
            private_value = row_data[field_names.VALUES]

            if private_label and set_labels:

                indented_label = (indent * " ") + private_label

                self._set_label(
                    sheet=sheet,
                    label=indented_label,
                    row=sheet.bb.current_row,
                    column=label_column
                    )

            self._group_lines(sheet)

            param_cell = sheet.cell(column=period_column,
                                    row=sheet.bb.current_row)

            cell_styles.format_parameter(param_cell)
            cell_styles.format_hardcoded(param_cell)

            if isinstance(private_value, (list, set, dict, map)):
                private_value = str(private_value)
                # Capture mutable and multi-dimensional objects here. We need
                # to figure out how to represent them in Excel later.

            param_cell.value = private_value

            relative_position = sheet.bb.current_row - \
                                (private_data.rows.starting or 0)
            private_data.rows.by_name[private_label] = relative_position
            # ... In this particular case, we could map a specific cell
            # (in memory) to the parameter. Unclear whether that's useful
            # though, because we generally look up locations for lines, not
            # parameters. And lines continue to span several rows.

            sheet.bb.current_row += 1
            # Will add a blank row after all the columns

        # Transform the range values from rows to coordinates
        param_coordinates = self._rows_to_coordinates(
            lookup=private_data.rows,
            column=period_column)

        # Apply param:var conversions so formula can find its expected inputs
        for param_name, var_name in driver_data.conversion_map.items():
            param_coordinates[var_name] = param_coordinates[param_name]

        # Finally, format the formula as necessary
        # (if references are a dict of objects, could map each obj to its
        #  coordinates)
        line_coordinates = dict()
        for k, obj in driver_data.references.items():
            line_coordinates[k] = obj.xl.get_coordinates()

        materials = dict()
        materials["lines"] = line_coordinates
        materials[field_names.PARAMETERS] = param_coordinates

        life_coordinates = self._rows_to_coordinates(
            lookup=sheet.bb.life.rows,
            column=period_column)
        materials["life"] = life_coordinates

        event_coordinates = self._rows_to_coordinates(
            lookup=sheet.bb.events.rows,
            column=period_column)
        materials["events"] = event_coordinates
        materials["steps"] = dict()

        n_items = len(driver_data.formula.items())
        count = 0
        for key, template in driver_data.formula.items():
            count += 1

            try:
                formula = template.format(**materials)
            except Exception as X:
                print("Name:     ", driver_data.name)
                print("Template: ", driver_data.formula)
                raise ExcelPrepError

            calc_cell = sheet.cell(column=period_column,
                                   row=sheet.bb.current_row)
            calc_cell.set_explicit_value(formula, data_type=type_codes.FORMULA)

            # add current step to materials dictionary
            materials["steps"][key] = calc_cell.coordinate

            if set_labels and (COMMENT_FORMULA_NAME or
                               COMMENT_FORMULA_STRING or
                               COMMENT_CUSTOM):
                c = ""

                if COMMENT_FORMULA_NAME:
                    c += "Formula name: " + driver_data.name + "\n"

                if COMMENT_FORMULA_STRING:
                    c += "Formula string: " + template + "\n"

                if COMMENT_CUSTOM:
                    c += "Comment: " + driver_data.comment + "\n"

                a = "LineChef"
                calc_cell.comment = Comment(c, a)

            cell_styles.format_calculation(calc_cell)
            # If formula included a reference to the prior value of the line
            # itself, it's picked up here. Can now change line.xl.derived.final
            line.xl.derived.ending = sheet.bb.current_row
            line.xl.derived.cell = calc_cell

            self._group_lines(sheet)

            if set_labels:
                label = (indent * " ") + key # driver_data.name
                self._set_label(sheet=sheet, label=label,
                                row=sheet.bb.current_row)

            # we don't want a blank row between the calc cell and the summary
            # cell
            if count < n_items:
                sheet.bb.current_row += 1

        sheet.bb.outline_level -= 1

        return sheet

    def _add_reference(self, *pargs, sheet, column, line,
                              set_labels=True, indent=0):
        """


        LineChef._add_reference() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Adds a single cell reference to a new cell.
        (e.g. new_cell.value = '=C18')
        """
        if not line.xl.reference.source:
            pass

        else:
            sheet.bb.current_row += 1
            cell = sheet.cell(column=column, row=sheet.bb.current_row)

            ref_cell = line.xl.reference.source.xl.cell
            excel_str = "="+line.xl.reference.source.xl.get_coordinates()

            cell.set_explicit_value(excel_str, data_type=type_codes.FORMULA)

            label = indent*" " + line.tags.name

            line.xl.ending = sheet.bb.current_row
            line.xl.cell = cell
            line.xl.reference.cell = ref_cell

            if set_labels:
                self._set_label(label=label, sheet=sheet,
                                row=sheet.bb.current_row)

        return sheet

    def _combine_segments(self, *pargs, sheet, column, line, set_labels=True,
                          indent=0):
        """


        LineChef._combine_segments() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Adds the combination to the current row.
        """
        sheet.bb.current_row += 1
        cell = sheet.cell(column=column, row=sheet.bb.current_row)

        ends = [
            line.xl.consolidated.ending,
            line.xl.derived.ending,
            line.xl.detailed.ending
                     ]

        segment_summation = self._sum_endpoints(rows=ends, column=column)

        if segment_summation:
            cell.set_explicit_value(segment_summation,
                                    data_type=type_codes.FORMULA)

            label = indent*" " + LineItem.SUMMARY_PREFIX + line.tags.name
        else:
            # Blank or hard-coded line
            cell.value = line.value
            cell_styles.format_hardcoded(cell)

            label = indent*" " + line.tags.name

        line.xl.ending = sheet.bb.current_row
        line.xl.cell = cell

        self._group_lines(sheet)

        if set_labels:
            label_column = None
            if not getattr(sheet.bb, "parameters", None):
                label_column = 1

            self._set_label(label=label, sheet=sheet, row=sheet.bb.current_row,
                            column=label_column)

        return sheet

    @staticmethod
    def _group_lines(sheet):
        """


        LineChef._group_lines() -> None

        --``sheet`` must be an instance of openpyxl Worksheet

        Tell Excel to group lines and collapse
        Delegates to method from _chef_tools
        """
        group_lines(sheet)

    def _rows_to_coordinates(self, *pargs, lookup, column):
        """


        LineChef._rows_to_coordinates -> dict

        --``lookup`` is a lookup table
        --``column`` must be a column number reference

        Method returns a dictionary of row name:row coordinate within the given
        column.
        """

        result = dict()
        alpha_column = get_column_letter(column)

        for k in lookup.by_name:
            row = lookup.get_position(k)
            result[k] = alpha_column + str(row)

        return result

    def _set_label(self, *pargs, label, sheet, row, column=None,
                   overwrite=False):
        """


        LineChef._set_label() -> Worksheet

        --``label`` must be value to set as a cell label
        --``sheet`` must be an instance of openpyxl Worksheet
        --``row`` must be a row index where ``label`` should be written
        --``column`` column index or None where ``label`` should be written
        --``overwrite`` must be a boolean; True overwrites existing value,
           if any; default is False

        Set (column, row) cell value to label. Throw exception if cell already
        has a different label, unless ``overwrite`` is True.

        If ``column`` is None, method attempts to locate the labels column in
        the sheet.bb.parameters area.
        """
        if column is None:
            column=sheet.bb.parameters.columns.get_position(field_names.LABELS)

        label_cell = sheet.cell(column=column, row=row)
        existing_label = label_cell.value

        if overwrite or not existing_label:
            label_cell.value = label
        else:
            if existing_label != label:

                c = """
                Something is wrong with our alignment. We are trying to
                write a parameter to an existing row with a different label."""

                raise Error(c)

                # Check to make sure we are writing to the right row; if the
                # label doesn't match, we are in trouble.

        return sheet

    def _sum_endpoints(self, *pargs, rows, column):
        """


        LineChef._sum_endpoints() -> string

        --``row`` must be a row index where ``label`` should be written
        --``column`` column index or None where ``label`` should be written

        Return a summation of each of the rows in column. Expects rows to be a
        collection of absolute row indices.
        """
        summation = ""

        coordinates = dict()
        coordinates["alpha_column"] = get_column_letter(column)

        for row in rows:
            if row is not None:
                coordinates["row"] = row
                link = formula_templates.ADD_CELL.format(**coordinates)
                summation += link

        return summation
