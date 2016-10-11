# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.data_types
"""

Module defines a class that stores explicit data type codes compatible with the
Excel cell.set_explicit_value(data_type) interface and explicit number format
codes.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TypeCodes             known cell data types
NumberFormats         formats for numbers
====================  =========================================================
"""




# Imports
from openpyxl.styles import numbers

from chef_settings import PARAM_DECIMAL_POINTS




# Constants
# n/a

# Module Globals
# n/a

# Classes
class TypeCodes:
    """

    Class stores type strings known to the excel interface.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    BOOL                  type code for boolean value
    FORMULA               forces Excel to try and interpret string as a formula
    FORMULA_CACHE_STRING  type code for string value
    NUMERIC               type code for numeric value

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    BOOL = "b"
    FORMULA = "f"
    FORMULA_CACHE_STRING = "str"
    NUMERIC = "n"


class NumberFormats:
    """

    Class stores type strings for number formats.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    DEFAULT_DATE_FORMAT   "yyyy-mm-dd"; format code for datetime
    DEFAULT_LINE_FORMAT   $#,###.##
    DEFAULT_PARAMETER_FORMAT  "#,##0"
    INTEGER_FORMAT         Excel number format

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    DEFAULT_DATE_FORMAT = numbers.FORMAT_DATE_YYYYMMDD2
    DEFAULT_LINE_FORMAT = numbers.FORMAT_CURRENCY_USD_SIMPLE

    DEFAULT_PARAMETER_FORMAT = "#,##0"
    if PARAM_DECIMAL_POINTS > 0:
        DEFAULT_PARAMETER_FORMAT += "."
        DEFAULT_PARAMETER_FORMAT += "0" * PARAM_DECIMAL_POINTS

    INTEGER_FORMAT = numbers.FORMAT_NUMBER
