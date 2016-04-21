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

from openpyxl.styles import Border, Side, Font, numbers
from openpyxl.styles.colors import RED, BLACK, BLUE




# Constants
# n/a

# Module Globals
DEFAULT_DATE_FORMAT = numbers.FORMAT_DATE_YYYYMMDD2
DEFAULT_LINE_FORMAT = numbers.FORMAT_CURRENCY_USD_SIMPLE
DEFAULT_PARAMETER_FORMAT = numbers.FORMAT_GENERAL

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

        use_format = line.xl.number_format or DEFAULT_LINE_FORMAT

        if line.xl.derived.cell:
            line.xl.derived.cell.number_format = use_format

        if line.xl.consolidated.cell:
            line.xl.consolidated.cell.number_format = use_format

        if line.xl.detailed.cell:
            line.xl.detailed.cell.number_format = use_format

        if line.xl.cell:
            line.xl.cell.number_format = use_format

    @staticmethod
    def format_hardcoded(cell):
        font = Font(color=BLUE)
        cell.font = font

    @staticmethod
    def format_calculation(cell):
        pass

    @staticmethod
    def format_parameter(cell):
        pass

    @staticmethod
    def format_accounting(cell):
        cell.number_format = DEFAULT_LINE_FORMAT

    @staticmethod
    def format_date(cell):
        cell.number_format = DEFAULT_DATE_FORMAT

    @staticmethod
    def format_area_label(cell):
        pass