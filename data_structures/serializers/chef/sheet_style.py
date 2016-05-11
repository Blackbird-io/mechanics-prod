# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.cell_styles
"""

Module defines a class that stores standard row and column names.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SheetStyle            standard styles for worksheets
====================  =========================================================
"""




# Imports
import openpyxl as xlio

from .cell_styles import CellStyles
from .chef_settings import COLUMN_WIDTH
from .field_names import FieldNames

# Constants
SHOW_GRID_LINES = False
ZOOM_SCALE = 80

# Module Globals
cell_styles = CellStyles()
field_names = FieldNames()
get_column_letter = xlio.utils.get_column_letter

# Classes
class SheetStyle:
    """

    Class stores standard keys for row and column lookups within SheetData.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """

    def style_sheet(self, sheet):
        self.label_areas(sheet)

        sheet.sheet_view.showGridLines = SHOW_GRID_LINES
        sheet.sheet_view.zoomScale = ZOOM_SCALE

    @staticmethod
    def label_areas(sheet):
        areas_exclude = set((field_names.GENERAL, field_names.TIMELINE))
        areas = set(sheet.bb.area_names)
        areas = areas - areas_exclude

        for name in areas:
            area = getattr(sheet.bb, name)
            if not area.rows.by_name:
                continue

            row_num = min(area.rows.by_name.values()) - 1
            cell_styles.format_area_label(sheet, name, row_num)

    @staticmethod
    def set_column_width(sheet, column):
        column = sheet.column_dimensions[get_column_letter(column)]
        column.width = COLUMN_WIDTH