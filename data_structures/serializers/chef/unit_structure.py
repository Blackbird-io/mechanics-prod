# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.unit_structure
"""

Module defines a class for displaying the company structure in Excel.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
StructureChef         class containing methods to display BusinessUnits
                      components on a sheet
====================  =========================================================
"""




# Imports
from openpyxl.styles import Border, Side, Alignment

import chef_settings

from .tab_names import TabNames
from .sheet_style import SheetStyle




# Constants
# n/a

# Module Globals
# n/a


# Classes
class StructureChef:
    """
    Creates a tab that lays out component structure.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    BOX_HEIGHT            box sizing
    BOX_ACROSS            box sizing

    FUNCTIONS:
    chop()                creates a tab for unit structure
    unit_box()            creates a top-level box and recurs to components
    layout()              once all boxes are set, computes the layout
    ====================  =====================================================
    """
    BOX_HEIGHT = 2
    BOX_ACROSS = 2

    def chop(self, book, unit, level=0):
        """


        StructureChef.chop() -> None

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit

        Method recursively walks through ``unit`` and components and displays
        a diagram of BU structure on an Excel sheet.
        """
        # sheet location
        ahead = book.get_sheet_by_name(TabNames.SCENARIOS)
        index = book.get_index(ahead) + 1

        # sheet layout
        sheet = book.create_sheet(TabNames.STRUCTURE, index)
        sheet.sheet_properties.tabColor = chef_settings.COVER_TAB_COLOR
        SheetStyle.style_sheet(sheet)

        header_rows = sheet.bb.row_axis.add_group('header', size=1)
        header_cols = sheet.bb.col_axis.add_group('header', size=1)
        body_rows = sheet.bb.row_axis.add_group('body')
        body_cols = sheet.bb.col_axis.add_group('body')

        # start with top box
        self.unit_box(sheet, unit, body_rows, body_cols, level=0)
        body_rows.calc_size()
        body_cols.calc_size()
        self.layout(sheet, body_cols.groups)

    def unit_box(self, sheet, unit, row_container, col_container, level=0):
        """


        StructureChef.unit_box() -> None

        --``sheet`` must be a Worksheet
        --``unit`` must be an instance of BusinessUnit

        Method recursively walks through ``unit`` creating a nested column
        layout for unit boxes.
        """
        # row is determined by depth
        unit_rows = row_container.add_group(
            level,
            offset=2 if level else 0,
            size=self.BOX_HEIGHT,
        )
        # column is determined by parent unit
        unit_cols = col_container.add_group(
            unit.title,
            offset=1 if col_container.groups else 0,
            rows=unit_rows,
            label=unit.title,
        )

        children = unit.components.get_ordered()
        if children:
            for child in children:
                self.unit_box(
                    sheet, child, row_container, unit_cols, level=level + 1
                )
        else:
            unit_cols.size = self.BOX_ACROSS

    def layout(self, sheet, groups, level=0):
        """


        StructureChef.layout() -> None

        Method adds boxes.
        """
        for group in groups:
            unit_rows = group.extra['rows']
            if group.groups:
                self.layout(
                    sheet, group.groups, level=level + 1
                )
            self._make_cell(sheet, unit_rows, group)

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                              #
    # *************************************************************************#

    def _make_cell(self, sheet, row_container, col_container):
        """

        StructureChef._make_cell() -> None

        """
        center_col = int(col_container.size / 2) + col_container.number()
        # for 2-col box, 1 left of center_col
        col_tip = center_col - int(self.BOX_ACROSS / 2)
        row = row_container.number()
        label = col_container.extra.get('label')

        # all the cells that will be mered into a combined cell
        box = []
        side = Side(border_style='double')
        border = Border(left=side, right=side, top=side, bottom=side)
        for yspan in range(self.BOX_HEIGHT):
            box.append([])
            for xspan in range(self.BOX_ACROSS):
                c = sheet.cell(row=row + yspan, column=col_tip + xspan)
                c.border = border
                box[-1].append(c)
        sheet.merge_cells(
            start_row=row, start_column=col_tip,
            end_row=row + 1, end_column=col_tip + 1
        )

        # value and styling of the merged cell
        cell = box[0][0]
        cell.value = label
        cell.alignment = Alignment(
            wrapText=True, vertical='center', horizontal='center'
        )

        # draw connecting lines
        col_container.extra['center'] = center_col
        if col_container.groups:
            self._child_line(
                sheet, row + self.BOX_HEIGHT, center_col, col_container.groups
            )

    def _child_line(self, sheet, row, center_col, groups):
        """

        StructureChef._child_line() -> None

        Draws lines from parent to children.
        """
        # stem from parent down to children
        side = Side(border_style='thick')
        upper = sheet.cell(row=row, column=center_col)
        upper.border = Border(left=side)
        under = sorted(g.extra['center'] for g in groups)

        # stems from children up to parent
        for col in under:
            c = sheet.cell(row=row + 1, column=col)
            border = c.border.copy()
            border.left = side
            c.border = border

        # branch on which children hang
        if len(under) > 1:
            tipcol = min(under)
            endcol = max(under)
            for col in range(tipcol, endcol):
                c = sheet.cell(row=row, column=col)
                border = c.border.copy()
                border.bottom = side
                c.border = border
