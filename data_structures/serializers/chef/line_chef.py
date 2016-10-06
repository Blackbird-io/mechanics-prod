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
import calendar
import openpyxl as xlio
import re
import itertools

from openpyxl.comments import Comment
from openpyxl.styles import Alignment

from bb_exceptions import ExcelPrepError, BBAnalyticalError
from chef_settings import (
    COMMENT_FORMULA_NAME, COMMENT_FORMULA_STRING,
    COMMENT_CUSTOM, BLANK_BETWEEN_TOP_LINES, FILTER_PARAMETERS,
    SUMMARY_INCLUDES_MONTHS, SUMMARY_INCLUDES_QUARTERS,
)
from data_structures.modelling.line_item import LineItem
from ._chef_tools import group_lines, check_alignment
from .cell_styles import CellStyles
from .data_types import TypeCodes
from .field_names import FieldNames
from .formulas import FormulaTemplates




# Constants
# n/a

# Module Globals





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
    attempt_reference_resolution() tries to resolve missing line refs in formulas
    chop_line()           writes LineItems to Excel
    chop_startbal_line()  writes LineItems from Starting Balance Sheet to Excel
    chop_starting_balance() writes Starting Balance Sheet to Excel
    chop_statement()      writes Statements to Excel (except Starting Balance)
    chop_summary_line()   writes LineItems from financial summaries to Excel
    chop_summary_statement() writes financial summary statements to Excel
    ====================  =====================================================
    """

    @staticmethod
    def attempt_reference_resolution(sheet, calc, materials):
        """
        Make new method for reevaluating problem lines and updating
         their line references.  Algorithm will look something like:
            - update line_coordinates dictionary (copy from below)
            - find first line where steps were written
            - reformat formulas using updated materials dict and save
              values
        """

        # Update materials
        new_lines = dict()
        for key, line in calc.references.items():
            try:
                include = line.xl.cell.parent is not sheet
                new_lines[key] = line.xl.get_coordinates(include_sheet=include)
            except (ExcelPrepError, AttributeError):
                print("Name:     ", calc.name)
                print("Template: ", calc.formula)
                print(line)

                msg = 'Cannot resolve bad line reference.'
                raise ExcelPrepError(msg)

        materials['lines'] = new_lines

        # now reformat all formulas in steps
        for step in calc.formula:
            # see if step in materials['steps'], if not, it was purposely
            # omitted so skip it!
            if step not in materials['steps']:
                continue

            cell_coos = materials['steps'][step]
            cell = sheet[cell_coos]

            formula_string = calc.formula[step]
            try:
                formula_string = formula_string.format(**materials)
            except Exception as X:
                print("Name:     ", calc.name)
                print("Step:     ", step)
                print("Template: ", formula_string)

                raise ExcelPrepError

            cell.set_explicit_value(formula_string,
                                    data_type=TypeCodes.FORMULA)

    def chop_line(
        self, sheet, column, line, row_container,
        set_labels=True, indent=0, check=True
    ):
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
        details = line.get_ordered()

        if line.xl.format.blank_row_before and not details:
            sheet.bb.need_spacer = True
        if sheet.bb.need_spacer:
            if not row_container.offset:
                row_container.tip += 1
                row_container.offset = 1
            sheet.bb.current_row += 1
            sheet.bb.need_spacer = False

        # a line with own content should have no children with own content,
        # and should not consolidate
        line.has_own_content = any((
            len(details) > 0,
            line.xl.derived.calculations,
            line.hardcoded,
        ))

        sheet.bb.current_row = row_container.tip

        row_group = row_container.add_group('reference')
        self._add_reference(
            sheet=sheet,
            column=column,
            line=line,
            set_labels=set_labels,
            indent=indent
        )
        row_group.size = sheet.bb.current_row - row_group.tip

        row_group = row_container.add_group('derivation')
        self._add_derivation_logic(
            sheet=sheet,
            column=column,
            line=line,
            set_labels=set_labels,
            indent=indent + LineItem.TAB_WIDTH
        )
        row_group.size = sheet.bb.current_row - row_group.tip

        if line.has_own_content:
            # throw an error if any of consolidation sources have content
            self._validate_consolidation(sheet, line)
        else:
            row_group = row_container.add_group('consolidation')
            self._add_consolidation_logic(
                sheet=sheet,
                column=column,
                line=line,
                set_labels=set_labels,
                indent=indent + LineItem.TAB_WIDTH
            )
            row_group.size = sheet.bb.current_row - row_group.tip

        if details:
            sub_indent = indent + LineItem.TAB_WIDTH
            detail_summation = ""
            detail_group = row_container.add_group('details')

            for detail in details:
                detail_rows = detail_group.add_group(detail.name)
                sheet.bb.outline_level = 0
                self.chop_line(
                    sheet=sheet,
                    column=column,
                    line=detail,
                    row_container=detail_rows,
                    set_labels=set_labels,
                    indent=sub_indent,
                    check=check
                )

                link_template = FormulaTemplates.ADD_COORDINATES

                include = detail.xl.cell.parent is not sheet
                cos = detail.xl.get_coordinates(include_sheet=include)
                link = link_template.format(coordinates=cos)
                detail_summation += link
            else:
                detail_group.calc_size()

                if line.xl.format.blank_row_before:
                    sheet.bb.current_row += 1
                    row_container.add_group('spacer_details', size=1)

                row_container.add_group('details_summary', size=1)

                # Should group all the details here
                sheet.bb.current_row += 1
                sheet.bb.outline_level = 0

                subtotal_cell = sheet.cell(column=column,
                                           row=sheet.bb.current_row)
                subtotal_cell.set_explicit_value(detail_summation,
                                                 data_type=TypeCodes.FORMULA)

                line.xl.detailed.ending = sheet.bb.current_row
                line.xl.detailed.cell = subtotal_cell
                line.xl.cell = subtotal_cell

                if set_labels:
                    label = indent * " " + line.tags.title
                    self._set_label(sheet=sheet,
                                    label=label,
                                    row=sheet.bb.current_row)

        if not line.xl.reference.source:
            segment_group = row_container.add_group('segments')
            self._combine_segments(
                sheet=sheet,
                column=column,
                line=line,
                set_labels=set_labels,
                indent=indent)
            segment_group.size = sheet.bb.current_row - segment_group.tip

        CellStyles.format_line(line)

        # for row alignment
        if check:
            check_alignment(line)

        if line.id.bbid not in sheet.bb.line_directory.keys():
            sheet.bb.line_directory[line.id.bbid] = line.xl

        if line.xl.format.blank_row_after:
            sheet.bb.need_spacer = True

        row_container.calc_size()
        return sheet

    def chop_startbal_line(self, *pargs, sheet, column, line, set_labels=True,
                           indent=0):
        """


        LineChef.chop_startbal_line() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Method walks through LineItems and their details and converts them to
        dynamic links in Excel cells.  Method method links line to itself if
        already chopped (starting balance sheets are pointed to previous period
        ending balance sheets during BusinessUnit._load_balance()), or will
        strictly print value.  Specific logic for starting balance sheet.

        Method relies on sheet.bb.current_row being up-to-date.

        Routines deliver sheet with the current_row pointing to the last filled
        in cell.
        """
        details = line.get_ordered()

        if line.xl.format.blank_row_before and not details:
            sheet.bb.current_row += 1

        if details:
            sub_indent = indent + LineItem.TAB_WIDTH
            detail_summation = ""

            for detail in details:
                sheet.bb.outline_level = 0
                self.chop_startbal_line(sheet=sheet,
                                        column=column,
                                        line=detail,
                                        set_labels=set_labels,
                                        indent=sub_indent)

                link_template = FormulaTemplates.ADD_COORDINATES

                include = detail.xl.cell.parent is not sheet
                cos = detail.xl.get_coordinates(include_sheet=include)
                link = link_template.format(coordinates=cos)
                detail_summation += link
            else:
                if line.xl.format.blank_row_before:
                    sheet.bb.current_row += 1

                # Should group all the details here
                sheet.bb.current_row += 1

                subtotal_cell = sheet.cell(column=column,
                                           row=sheet.bb.current_row)
                subtotal_cell.set_explicit_value(detail_summation,
                                                 data_type=TypeCodes.FORMULA)

                line.xl.detailed.ending = sheet.bb.current_row
                line.xl.detailed.cell = subtotal_cell
                line.xl.cell = subtotal_cell

                if set_labels:
                    label_column = None
                    if not getattr(sheet.bb, FieldNames.PARAMETERS, None):
                        label_column = 1

                    label = indent * " " + line.tags.title
                    self._set_label(sheet=sheet,
                                    label=label,
                                    row=sheet.bb.current_row,
                                    column=label_column)

            CellStyles.format_line(line)
        else:
            if line.xl.cell:
                # here just link the current cell to the cell in line.xl.cell
                old_cell = line.xl.cell
                line.xl.reference.source = line
                self._add_reference(
                    sheet=sheet,
                    column=column,
                    line=line,
                    set_labels=set_labels,
                    indent=indent)

                CellStyles.format_line(line)

                line.xl.reference.source = None
                line.xl.reference.cell = None
                line.xl.cell = old_cell
            else:
                self._combine_segments(
                    sheet=sheet,
                    column=column,
                    line=line,
                    set_labels=set_labels,
                    indent=indent)

                CellStyles.format_line(line)

        if line.xl.format.blank_row_after:
            sheet.bb.current_row += 1

    def chop_starting_balance(
        self, sheet, column, unit, row_container, set_labels=True
    ):
        """


        LineChef.chop_starting_balance() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``statement`` must be an instance of Statement
        --``set_labels`` must be a boolean; True will set labels for line

        Method walks through starting balance lines and delegates to
        LineChef.chop_startbal_line() to add them as dynamic links in Excel.

        Method relies on sheet.bb.current_row being up-to-date.  Method logic
        specific to starting balance sheets.
        """
        statement = unit.financials.starting

        if not BLANK_BETWEEN_TOP_LINES:
            sheet.bb.current_row += 1

        for line in statement.get_ordered():
            if BLANK_BETWEEN_TOP_LINES:
                sheet.bb.current_row += 1

            line_rows = row_container.add_group(line.name)
            self.chop_startbal_line(sheet=sheet,
                                    column=column,
                                    line=line,
                                    set_labels=True)
            line_rows.size = sheet.bb.current_row - line_rows.tip

        sheet.bb.current_row += 1

        return sheet

    def chop_statement(
        self, sheet, column, statement, row_container=None, set_labels=True
    ):
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
        if not row_container:
            row_container = sheet.bb.row_axis.add_group(
                'body', 'statements', statement.title,
            )
            row_container.tip = sheet.bb.current_row + 1
            row_container.add_group('matter')
        matter = row_container.get_group('matter')

        if not BLANK_BETWEEN_TOP_LINES:
            sheet.bb.current_row += 1

        check = statement.name != 'ending balance sheet'
        for line in statement.get_ordered():
            if BLANK_BETWEEN_TOP_LINES:
                sheet.bb.current_row += 1

            offset = 1 if BLANK_BETWEEN_TOP_LINES else 0
            line_rows = matter.add_group(line.title, offset=offset)

            self.chop_line(
                sheet=sheet,
                column=column,
                line=line,
                row_container=line_rows,
                set_labels=set_labels,
                check=check
            )

        if len(statement.get_ordered()) == 0:
            sheet.bb.need_spacer = True
            sheet.bb.current_row += 1
        else:
            sheet.bb.need_spacer = False

        return sheet

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _add_detail(
        self, sheet, column, line, row_container, indent=0
    ):
        """


        LineChef._add_detail() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``indent`` is amount of indent
        --``row_container`` coordinate anchor on the row axis

        Displays detail sources.
        """
        details = line.get_ordered()
        if details:
            sub_indent = indent + LineItem.TAB_WIDTH
            detail_summation = ""
            detail_rows = row_container.add_group('details')

            for detail in details:
                self.chop_summary_line(
                    sheet=sheet,
                    column=column,
                    line=detail,
                    row_container=detail_rows,
                    indent=sub_indent
                )
                link_template = FormulaTemplates.ADD_COORDINATES
                include = detail.xl.cell.parent is not sheet
                cos = detail.xl.get_coordinates(include_sheet=include)
                link = link_template.format(coordinates=cos)
                detail_summation += link

            # group all the details here
            label = indent * " " + line.title
            detail_endrow = row_container.add_group(
                label, size=1, label=label
            )
            subtotal_cell = sheet.cell(
                column=column, row=detail_endrow.number()
            )
            subtotal_cell.set_explicit_value(
                detail_summation, data_type=TypeCodes.FORMULA
            )

            line.xl.detailed.ending = detail_endrow.tip
            line.xl.detailed.cell = subtotal_cell
            line.xl.cell = subtotal_cell

        return sheet

    def _validate_consolidation(self, sheet, line):
        """


        LineChef._validate_consolidation() -> None

        --``line`` must be an instance of LineItem

        Throws an error if all are true:
        1. ``line`` has own content: details, drivers, or value.
        2. ``line`` has consolidation sources.
        3. sources have own content.
        """

        if line.has_own_content:
            for sub in line.xl.consolidated.sources:
                if sub.has_own_content:
                    c = (
                        'line "{}" on sheet "{}" has content '
                        'but also tries to consolidate line "{} '
                        'which has its own content'
                    ).format(line.title, sheet.title, sub.title)

                    raise BBAnalyticalError(c)

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
            sources = line.xl.consolidated.sources
            labels = line.xl.consolidated.labels
            required_rows = sheet.bb.consolidation_size
            n_sources = len(sources)
            links_per_cell = n_sources // required_rows
            links_per_cell = max(1, links_per_cell)
            # Make sure we include at least 1 link per cell.

            link_template = FormulaTemplates.ADD_COORDINATES

            sheet.bb.current_row += 1
            sheet.bb.outline_level += 1

            line.xl.consolidated.starting = sheet.bb.current_row
            line.xl.consolidated.array.clear()

            # the outer iter converts the sorted list into an iterator
            # which is needed to chunk it by group
            paired = iter(sorted(zip(labels, sources)))
            # chunker gives (label, source) pairs in chunks of "links_per_cell".
            # Each hit returns a links_per_cell-sized tuple of tuples.
            chunker = itertools.repeat(paired, links_per_cell)
            for source_list in itertools.zip_longest(*chunker):
                batch_summation = ""

                for label, source_line in source_list:
                    if label:
                        sub_indent = indent + LineItem.TAB_WIDTH
                        label_line = (sub_indent * " ") + label
                    include = source_line.xl.cell.parent is not sheet
                    source_cos = source_line.xl.get_coordinates(
                        include_sheet=include
                    )
                    link = link_template.format(coordinates=source_cos)
                    batch_summation += link

                if batch_summation:
                    batch_cell = sheet.cell(column=column,
                                            row=sheet.bb.current_row)
                    batch_cell.set_explicit_value(
                        batch_summation,
                        data_type=TypeCodes.FORMULA
                    )

                    line.xl.consolidated.array.append(batch_cell)

                    if label:
                        self._set_label(
                            sheet=sheet,
                            label=label_line,
                            row=sheet.bb.current_row,
                            formatter=CellStyles.format_consolidated_label
                        )

                group_lines(sheet)

                # Move on to next row
                line.xl.consolidated.ending = sheet.bb.current_row
                sheet.bb.current_row += 1

            # Group the cells
            alpha_column = get_column_letter(column)
            summation_params = {
                "starting_row": line.xl.consolidated.starting,
                "ending_row": line.xl.consolidated.ending,
                "alpha_column": alpha_column
            }

            summation = FormulaTemplates.SUM_RANGE.format(**summation_params)
            summation_cell = sheet.cell(column=column,
                                        row=sheet.bb.current_row)
            summation_cell.set_explicit_value(summation,
                                              data_type=TypeCodes.FORMULA)

            line.xl.consolidated.cell = summation_cell
            line.xl.cell = summation_cell

            if set_labels:
                label = line.tags.title
                label = ((indent - LineItem.TAB_WIDTH) * " ") + label
                self._set_label(sheet=sheet, label=label,
                                row=sheet.bb.current_row)

            line.xl.consolidated.ending = sheet.bb.current_row

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
            self._set_param_rows(line, sheet)
            sheet.bb.outline_level += 1
            for data_cluster in line.xl.derived.calculations:

                sheet.bb.current_row += 1
                group_lines(sheet)

                self._add_driver_calculation(
                    sheet=sheet,
                    column=column,
                    line=line,
                    driver_data=data_cluster,
                    set_labels=set_labels,
                    indent=indent)

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
        private_data = getattr(sheet.bb, FieldNames.PARAMETERS).copy()
        # Set up a private range that's going to include both "shared" period &
        # unit parameters from the column and "private" driver parameters.

        param_area = getattr(sheet.bb, FieldNames.PARAMETERS)
        cols = param_area.columns
        label_column = cols.get_position(FieldNames.LABELS)
        period_column = column

        for row_data in sorted(driver_data.rows,
                               key=lambda x: x[FieldNames.LABELS]):

            private_label = row_data[FieldNames.LABELS]
            private_value = row_data[FieldNames.VALUES]

            if private_label and set_labels:

                indented_label = (indent * " ") + private_label

                self._set_label(
                    sheet=sheet,
                    label=indented_label,
                    row=sheet.bb.current_row,
                    column=label_column
                )

            group_lines(sheet)

            param_cell = sheet.cell(column=period_column,
                                    row=sheet.bb.current_row)

            CellStyles.format_parameter(param_cell)
            CellStyles.format_hardcoded(param_cell)

            if isinstance(private_value, (list, set, dict, map)):
                private_value = str(private_value)
                # Capture mutable and multi-dimensional objects here. We need
                # to figure out how to represent them in Excel later.

            param_cell.value = private_value

            relative_position = sheet.bb.current_row \
                - (private_data.rows.starting or 0)
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
        problem_line = False
        for k, obj in driver_data.references.items():
            try:
                include = obj.xl.cell.parent is not sheet
                line_coordinates[k] = obj.xl.get_coordinates(
                    include_sheet=include
                )
            except (ExcelPrepError, AttributeError):
                # set flag for saving problem line
                problem_line = True

                # as a temporary measure, introduce a placeholder for line
                # coordinates
                line_coordinates[k] = '###'  # placeholder

        materials = dict()
        materials["lines"] = line_coordinates
        materials['parameters'] = param_coordinates

        try:
            life_coordinates = self._rows_to_coordinates(
                lookup=sheet.bb.life.rows,
                column=period_column)
        except AttributeError:
            pass
        else:
            materials["life"] = life_coordinates

        try:
            event_coordinates = self._rows_to_coordinates(
                lookup=sheet.bb.events.rows,
                column=period_column)
        except AttributeError:
            pass
        else:
            materials["events"] = event_coordinates

        try:
            size = getattr(sheet.bb, FieldNames.SIZE)
            size_coordinates = self._rows_to_coordinates(lookup=size.rows,
                                                         column=period_column)
        except AttributeError:
            pass
        else:
            materials["size"] = size_coordinates

        materials["steps"] = dict()

        n_items = len(driver_data.formula.items())
        count = 0

        formula_steps = self._get_formula_steps(driver_data, line, sheet)
        for key in formula_steps:
            count += 1

            try:
                template = driver_data.formula[key]
            except KeyError:
                sheet.bb.current_row += 1
                continue

            try:
                formula = template.format(**materials)
            except Exception as X:
                print("Name:     ", driver_data.title)
                print("Template: ", driver_data.formula)

                raise ExcelPrepError

            calc_cell = sheet.cell(column=period_column,
                                   row=sheet.bb.current_row)
            calc_cell.set_explicit_value(formula, data_type=TypeCodes.FORMULA)

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

            CellStyles.format_calculation(calc_cell)
            # If formula included a reference to the prior value of the line
            # itself, it's picked up here. Can now change line.xl.derived.final

            # we don't want a blank row between the calc cell and the summary
            # cell
            line.xl.derived.ending = sheet.bb.current_row
            line.xl.derived.cell = calc_cell
            line.xl.cell = calc_cell

            if problem_line:
                # save tuple of line and derivation materials
                info = (driver_data, materials)
                sheet.bb.problem_lines.append(info)

            if count < n_items:
                group_lines(sheet)

                if set_labels:
                    label = (indent * " ") + key
                    self._set_label(sheet=sheet, label=label,
                                    row=sheet.bb.current_row)

                sheet.bb.current_row += 1
            else:
                sheet.bb.outline_level = 0
                group_lines(sheet)

                if set_labels:
                    label = ((indent - LineItem.TAB_WIDTH) * " ") \
                        + line.tags.title
                    self._set_label(sheet=sheet, label=label,
                                    row=sheet.bb.current_row)

        return sheet

    def _add_reference(
        self, sheet, column, line,
        set_labels=True, indent=0, update_cell=True, row_container=None
    ):
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
        if line.xl.reference.source:
            label = indent * " " + line.tags.title
            if row_container:
                row_container.add_group(line.title, size=1, label=label)
                sheet.bb.current_row = row_container.number()
            else:
                sheet.bb.current_row += 1
            cell = sheet.cell(column=column, row=sheet.bb.current_row)

            ref_cell = line.xl.reference.source.xl.cell
            include = ref_cell.parent is not sheet
            source = line.xl.reference.source
            excel_str = "=" + source.xl.get_coordinates(include_sheet=include)

            cell.set_explicit_value(excel_str, data_type=TypeCodes.FORMULA)

            line.xl.ending = sheet.bb.current_row
            line.xl.reference.cell = ref_cell

            if update_cell:
                line.xl.cell = cell

            if set_labels:
                self._set_label(label=label, sheet=sheet,
                                row=sheet.bb.current_row)

        return sheet

    def _combine_segments(
        self, sheet, column, line,
        set_labels=True, indent=0, row_container=None
    ):
        """


        LineChef._combine_segments() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``column`` must be a column number reference
        --``line`` must be an instance of LineItem
        --``set_labels`` must be a boolean; True will set labels for line
        --``indent`` is amount of indent

        Adds the combination to the current row.
        """
        processed = line.xl.consolidated.cell or line.xl.derived.cell or \
            line.xl.detailed.cell or line.xl.reference.cell

        if not processed:
            label = indent * " " + line.title
            if row_container:
                row_container.add_group(label, size=1, label=label)
                sheet.bb.current_row = row_container.number()
            else:
                sheet.bb.current_row += 1
            cell = sheet.cell(column=column, row=sheet.bb.current_row)

            # Blank or hard-coded line
            cell.value = line.value
            CellStyles.format_hardcoded(cell)

            line.xl.ending = sheet.bb.current_row
            line.xl.cell = cell

            if set_labels:
                self._set_label(label=label, sheet=sheet,
                                row=sheet.bb.current_row)

        return sheet

    @staticmethod
    def _get_formula_steps(driver_data, line, sheet):
        """

        Function gets and returns steps in formula calculation based on the
        template calculation for this line.
        """
        try:
            template_xl = sheet.bb.line_directory[line.id.bbid]
        except KeyError:
            template_xl = None

        if template_xl:
            # find template_driver_data where name = driver_data.name
            for check_data in template_xl.derived.calculations:
                if check_data.name == driver_data.name:
                    keys = check_data.formula.keys()
                    break
        else:
            keys = driver_data.formula.keys()

        return keys

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
                   overwrite=False,
                   formatter=None):
        """


        LineChef._set_label() -> Worksheet

        --``label`` must be value to set as a cell label
        --``sheet`` must be an instance of openpyxl Worksheet
        --``row`` must be a row index where ``label`` should be written
        --``column`` column index or None where ``label`` should be written
        --``overwrite`` must be a boolean; True overwrites existing value,
           if any; default is False
        --``formatter`` method in cell_styles to be called on the label cell

        Set (column, row) cell value to label. Throw exception if cell already
        has a different label, unless ``overwrite`` is True.

        If ``column`` is None, method attempts to locate the labels column in
        the sheet.bb.parameters area.
        """
        if column is None:
            if getattr(sheet.bb, FieldNames.PARAMETERS, None):
                param_area = getattr(sheet.bb, FieldNames.PARAMETERS)
                cols = param_area.columns
                column = cols.get_position(FieldNames.LABELS)
            else:
                column = 2

        label_cell = sheet.cell(column=column, row=row)
        existing_label = label_cell.value

        if overwrite or not existing_label:
            label_cell.value = label
        else:
            if existing_label != label:

                c = """
                Something is wrong with our alignment. We are trying to
                write a parameter to an existing row with a different label.
                """
                print(c)
                print("Old Label:", existing_label)
                print("New Label:", label)
                print("Sheet:", sheet.title)
                print("Row:", row)
                print("Col:", column)

                # raise ExcelPrepError(c)
                # Check to make sure we are writing to the right row; if the
                # label doesn't match, we are in trouble.

        if formatter:
            formatter(label_cell)

        return sheet

    @staticmethod
    def _set_param_rows(line, sheet):
        try:
            template_xl = sheet.bb.line_directory[line.id.bbid]
        except KeyError:
            template_xl = None

        if template_xl:
            for check_data, driver_data in zip(template_xl.derived.calculations,
                                               line.xl.derived.calculations):
                if check_data.name != driver_data.name:
                    c = "Formulas are not consistent for line over time!"
                    raise ExcelPrepError(c)

                driver_data.rows = check_data.rows
        elif FILTER_PARAMETERS:
            # get params to keep
            for driver_data in line.xl.derived.calculations:
                params_keep = []
                for step in driver_data.formula.values():
                    temp_step = [m.start() for m in re.finditer('parameters\[*',
                                                                step)]

                    for idx in temp_step:
                        jnk = step[idx:]
                        idx_end = jnk.find(']') + idx
                        params_keep.append(step[idx + 11:idx_end])

            # clean driver_data
            new_rows = []
            for item in driver_data.rows:
                if item[FieldNames.LABELS] in params_keep:
                    new_rows.append(item)

                try:
                    temp = driver_data.conversion_map[item[FieldNames.LABELS]]
                except KeyError:
                    pass
                else:
                    if temp in params_keep:
                        new_rows.append(item)

            driver_data.rows = new_rows
