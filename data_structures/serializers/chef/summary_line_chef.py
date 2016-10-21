# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.summary_line_chef
"""

Module defines SummaryLineChef class which converts Statement and LineItem
objects into dynamic Excel format.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SummaryLineChef       class with methods to chop BB statements into dynamic
                      Excel structures
====================  =========================================================
"""




# Imports
from data_structures.modelling.line_item import LineItem

from .cell_styles import CellStyles
from .delayed_cell import DelayedCell




# Constants
# n/a

# Module Globals

# Classes
class SummaryLineChef:
    """

    Class packages Statement and LineItem objects into dynamic Excel workbook.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    chop_summary_statement() writes financial summary statements to Excel
    chop_summary_line()   writes LineItems from financial summaries to Excel
    ====================  =====================================================
    """

    def chop_summary_statement(
        self, sheet, statement, row_container, col_container, title=None
    ):
        """


        SummaryLineChef.chop_summary_statement() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``statement`` must be an instance of Statement
        --``row_container`` is an instance of AxisGroup
        --``col_container`` is an instance of AxisGroup
        --``title`` str; optional string title to use

        Method walks through summary Statement lines and delegates to
        SummaryLineChef.chop_summary_line() to add them as dynamic links
        in Excel.
        """
        # sub-container for this statement
        title = title or statement.title
        statement_rows = row_container.add_group(
            title,
            # add a spacer between self and previous statement, if not first
            offset=1 if row_container.groups else 0,
        )

        # Add title row and statement body
        header = statement_rows.add_group('title', size=1, label=title)
        matter = statement_rows.add_group('lines')

        # if previous line wants blank_row_after, or this one blank_row_before
        sheet.bb.need_spacer = False

        for line in statement.get_ordered():
            self.chop_summary_line(
                sheet=sheet,
                line=line,
                row_container=matter,
                col_container=col_container,
            )

        return sheet

    def chop_summary_line(
        self, sheet, line, row_container, col_container, indent=0,
        show_empty=True,
    ):
        """


        SummaryLineChef.chop_summary_line() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``line`` must be an instance of LineItem
        --``row_container`` is an instance of AxisGroup
        --``indent`` is amount of indent
        --``show_empty`` bool; whether to show empty lines

        Method walks through LineItems and their details and converts them to
        dynamic links in Excel cells.  Method adds consolidation and derivation
        logic to cells.  Specific logic for lines from summaries.

        Routines deliver sheet with the current_row pointing to the last filled
        in cell.
        """
        # add an axis placeholder for this line
        matter = row_container.add_group(
            indent * " " + line.title,
            label=indent * " " + line.title,
        )

        # previous line may have requested a spacer after itself
        # or we want one before ourselves
        if line.xl.format.blank_row_before and not line._details:
            sheet.bb.need_spacer = True
        if sheet.bb.need_spacer:
            if not matter.offset:
                matter.offset = 1
            sheet.bb.need_spacer = False

        # sources of information for output
        for op in ((
            # link to another cell
            self._add_reference,
            # consolidation, time summary falls here
            self._add_consolidation,
            # details lines
            self._add_detail,
            # derived lines
            self._add_derivation,
            # catch-all if no content has been added so far
            self._add_value,
        )):
            op(
                sheet=sheet,
                line=line,
                row_container=matter,
                col_container=col_container,
                indent=indent,
            )

        if line.id.bbid not in sheet.bb.line_directory.keys():
            sheet.bb.line_directory[line.id.bbid] = line.xl

        if line.xl.format.blank_row_after:
            sheet.bb.need_spacer = True

        # if by tragic happenstance nothing has been added, setting
        # matter.size = 0 will drop the row
        # matter.size = 1 will add an empty row with a label
        if not matter.groups:
            matter.size = 1 if show_empty else 0

        return sheet

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _add_reference(
        self, sheet, line, row_container, col_container, indent=0
    ):
        """


        SummaryLineChef._add_reference() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``line`` must be an instance of LineItem
        --``indent`` is amount of indent
        --``row_container`` coordinate anchor on the row axis
        --``col_container`` coordinate anchor on the col axis

        Adds a pointer to an existing cell. Differs from _add_reference in
        adding references to derived as well as to reference cells.
        Will replace the original cell address that the line knows for itself
        with the new location.
        """
        source = None
        if line.xl.derived.calculations:
            source = line
        if line.xl.reference.source:
            source = line.xl.reference.source
        if source:
            cell = DelayedCell.from_cell(source)
            if cell:
                label = indent * " " + line.title
                matter = row_container.add_group(label, size=1, label=label)
                formula = '={ref}'
                sources = {'ref': cell}
                DelayedCell(
                    line,
                    sheet=sheet,
                    template=formula,
                    inputs=sources,
                    row_container=matter,
                    col_container=col_container,
                    cell_type='reference',
                )
                line.xl.ending = row_container.number()
        return sheet

    def _add_consolidation(
        self, sheet, line, row_container, col_container, indent=0
    ):
        """


        SummaryLineChef._add_consolidation() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``line`` must be an instance of LineItem
        --``indent`` is amount of indent
        --``row_container`` coordinate anchor on the row axis
        --``col_container`` coordinate anchor on the col axis

        Expects line.xl.consolidated.sources to include full range of pointers
        to source lines in relevant time periods.

        Creates a formula linking directly to TimeLine inputs.

        Returns Worksheet with consolidation logic added.
        """
        if line.xl.consolidated.sources:
            label = indent * " " + line.title  # + ': consolidation'
            matter = row_container.add_group(label, size=1, label=label)

            sources = line.xl.consolidated.sources
            labels = line.xl.consolidated.labels

            line.xl.consolidated.starting = matter.number()
            line.xl.consolidated.ending = matter.number()
            line.xl.consolidated.array.clear()

            formula_source = {}
            formula_layout = []
            for i, (label, source_line) in enumerate(zip(labels, sources)):
                cell = DelayedCell.from_cell(source_line)
                if cell:
                    formula_source['_{}'.format(i)] = cell
                    formula_layout.append('{{_{}}}'.format(i))
                    if source_line.xl.cell:
                        line.xl.consolidated.array.append(source_line.xl.cell)
            if formula_layout:
                formula = '+'.join(formula_layout)
                # handling for summary_type == 'average'
                if line.summary_type == 'average':
                    formula = '({})/{}'.format(formula, len(formula_source))
                formula = '={}'.format(formula)
                DelayedCell(
                    line,
                    sheet=sheet,
                    template=formula,
                    inputs=formula_source,
                    row_container=matter,
                    col_container=col_container,
                    cell_type='consolidated',
                )
        return sheet

    def _add_detail(
        self, sheet, line, row_container, col_container, indent=0
    ):
        """


        SummaryLineChef._add_detail() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``line`` must be an instance of LineItem
        --``indent`` is amount of indent
        --``row_container`` coordinate anchor on the row axis

        Displays detail sources.
        """
        details = line.get_ordered()
        if details:
            sub_indent = indent + LineItem.TAB_WIDTH
            detail_rows = row_container.add_group('details')

            formula_source = {}
            formula_layout = []
            for i, detail in enumerate(details):
                self.chop_summary_line(
                    sheet=sheet,
                    line=detail,
                    row_container=detail_rows,
                    col_container=col_container,
                    indent=sub_indent
                )
                cell = DelayedCell.from_cell(detail)
                if cell:
                    formula_source['_{}'.format(i)] = cell
                    formula_layout.append('{{_{}}}'.format(i))

            # aggregate line for the details
            label = indent * " " + line.title  # + ': details'
            detail_endrow = row_container.add_group(
                label, size=1, label=label
            )
            if formula_layout:
                formula = '=' + '+'.join(formula_layout)
                DelayedCell(
                    line,
                    sheet=sheet,
                    template=formula,
                    inputs=formula_source,
                    row_container=detail_endrow,
                    col_container=col_container,
                    cell_type='detailed',
                )

        return sheet

    def _add_value(
        self, sheet, line, row_container, col_container, indent=0
    ):
        """


        SummaryLineChef._add_value() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``line`` must be an instance of LineItem
        --``indent`` is amount of indent

        Adds line value to cell.
        """
        cell = DelayedCell.from_cell(line)
        if not cell:
            label = indent * " " + line.title
            matter = row_container.add_group(label, size=1, label=label)
            DelayedCell(
                line,
                sheet=sheet,
                value=line.value,
                row_container=matter,
                col_container=col_container,
                formatter=CellStyles.format_hardcoded,
            )

        return sheet

    def _add_derivation(
        self, sheet, line, row_container, col_container, indent=0
    ):
        """


        SummaryLineChef._add_derivation() -> Worksheet

        --``sheet`` must be an instance of openpyxl Worksheet
        --``line`` must be an instance of LineItem
        --``row_container`` coordinate anchor on the row axis
        --``col_container`` coordinate anchor on the col axis
        --``indent`` is amount of indent

        Creates a formula with driver logic. Only touches the lines where
            * there is a single calculation
            * there is a single formula line
            * all sources are lines
        """
        if not line.summary_type == 'derive':
            return
        if not line.xl.derived.calculations:
            return
        if len(line.xl.derived.calculations) != 1:
            return
        data_cluster = line.xl.derived.calculations[0]
        if len(data_cluster.formula) != 1:
            return
        # render first (and only) formula
        for key, formula in data_cluster.formula.items():
            # remap the DelayedCell input dict into '{lines[...]}' setup
            inputs_mold = lambda x: dict(lines=x)
            # input cells
            formula_source = {}
            # link to formula inputs
            for name, source_line in data_cluster.references.items():
                cell = DelayedCell.from_cell(source_line)
                if cell:
                    formula_source[name] = cell
            try:
                # check that we have enough inputs to render formula
                formula.format(**inputs_mold(formula_source))
            except KeyError:
                # not enough sources to render formula, defer to hardcoded
                return
            # create formula line
            line_label = indent * " " + line.title  # + ': derivation'
            finish = row_container.add_group(
                line_label, size=1, label=line_label
            )
            # create cell
            DelayedCell(
                line,
                sheet=sheet,
                template=formula,
                inputs=formula_source,
                inputs_mold=inputs_mold,
                row_container=finish,
                col_container=col_container,
                cell_type='derived',
            )
            # first only
            break
        return sheet
