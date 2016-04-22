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
CellStyles            standard styles for worksheet cells
====================  =========================================================
"""




# Imports
import openpyxl as xlio

from openpyxl.styles import Border, Side, Font, Alignment

from .data_types import NumberFormats
from .data_types import TypeCodes


# Constants
HARDCODED_COLOR = '2d5986'
CALCULATION_COLOR = '707070'

# Module Globals
number_formats = NumberFormats()
type_codes = TypeCodes()


# Classes
class CellStyles:
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

    @staticmethod
    def format_line(line):
        """


        CellStyles.format_line -> None

        --``line`` is an instance of LineItem

        Format cells written to for the provided line to conform with Chef
        standard.
        """

        use_format = line.xl.number_format or number_formats.DEFAULT_LINE_FORMAT

        if line.xl.derived.cell:
            line.xl.derived.cell.number_format = use_format

        if line.xl.consolidated.cell:
            line.xl.consolidated.cell.number_format = use_format

        if line.xl.detailed.cell:
            line.xl.detailed.cell.number_format = use_format

        if line.xl.cell:
            line.xl.cell.number_format = use_format
            line.xl.cell.font = Font(bold=True)

    @staticmethod
    def format_hardcoded(cell):
        """


        CellStyles.format_hardcoded -> None

        --``cell`` is an instance of openpyxl cell class

        Format cells containing hardcoded values to conform with Chef standard.
        """

        font = Font(color=HARDCODED_COLOR)
        cell.font = font

    @staticmethod
    def format_calculation(cell):
        """


        CellStyles.format_calculation -> None

        --``cell`` is an instance of openpyxl cell class

        Format cells containing calculations to conform with Chef standard.
        """
        # font = Font(italic=True, color=CALCULATION_COLOR)
        # cell.font = font

        cell.number_format = number_formats.DEFAULT_PARAMETER_FORMAT

    @staticmethod
    def format_parameter(cell):
        """


        CellStyles.format_parameter -> None

        --``cell`` is an instance of openpyxl cell class

        Format cells containing parameters to conform with Chef standard.
        """
        cell.number_format = number_formats.DEFAULT_PARAMETER_FORMAT
        cell.alignment = Alignment(horizontal='right')

    @staticmethod
    def format_date(cell):
        """


        CellStyles.format_date -> None

        --``cell`` is an instance of openpyxl cell class

        Format cells containing dates to conform with Chef standard.
        """

        cell.number_format = number_formats.DEFAULT_DATE_FORMAT

    @staticmethod
    def format_area_label(sheet, label, row_num):
        """


        CellStyles.format_area_label -> None

        --``sheet`` is an instance of openpyxl.worksheet
        --``label`` is a the string name of the area to label
        --``row_num`` is the row number where the label should be inserted

        Format area/statement label and dividing border
        """
        side = Side(border_style='double')

        cell_cos = 'A%s' % row_num
        cell = sheet[cell_cos]
        cell.font = Font(bold=True)
        cell.set_explicit_value(label.title(),
                                data_type=type_codes.FORMULA_CACHE_STRING)

        rows = sheet.iter_rows(row_offset=row_num-1)
        row = rows.__next__()
        for cell in row:
            border = Border(top=cell.border.top)
            border.top = side
            cell.border = border
