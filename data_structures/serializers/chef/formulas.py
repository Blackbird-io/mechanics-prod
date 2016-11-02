# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.formulas
"""

Module defines a class that stores string templates for commonly used formulas.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
FormulaTemplates      string templates with named fields
====================  =========================================================
"""




# Imports
# n/a




# Constants
# n/a

# Module Globals
# n/a

# Classes
class FormulaTemplates:
    """

    Class holds template Excel formulas.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    SUM_ANYRANGE          "+SUM({top_cell}:{end_cell})"
    SUM_RANGE             "=SUM({alpha_column}{starting_row}:{alpha_column}
                           {ending_row})"
    SUM_RANGE_ON_SHEET    "+SUM({sheet}!{alpha_column}{starting_row}:{sheet}!
                           {alpha_column}{ending_row})"

    ADD_CELL               "+{alpha_column}{row}"
    ADD_CELL_FROM_SHEET    "+{sheet}!{alpha_column}{row}"
    ADD_COORDINATES        "+{coordinates}"

    LINK_TO_CELL_ON_SHEET  "={sheet}!{alpha_column}{row}"
    LINK_TO_COORDINATES    "={coordinates}"

    HLOOKUP                "=HLOOKUP({ref_coords},{start_coords}:{end_coords},{ref_row},False)"

    COMPUTE_AGE_IN_DAYS    "=IF({birth}, {ref_date}-{birth})"
    COMPUTE_AGE_IN_PERCENT "=IF({span}, ROUND({age}/{span}*100,0))"
    COMPUTE_SPAN_IN_DAYS   "=IF({death}, {death}-{birth})"
    IS_ALIVE               "=IF(AND({birth}<={ref_date},{ref_date}<{death}),
                            TRUE,FALSE)"
    REPORT_DELTA           "={actual}-{forecast}"
    REPORT_DIFF            '=IFERROR(({actual}-{forecast})/{forecast},
                                                              "{placeholder}")'
    FUNCTIONS:
    n/a
    ====================  =====================================================
    """

    # GENERIC
    SUM_ANYRANGE = "+SUM({top_cell}:{end_cell})"
    SUM_RANGE = "=SUM({alpha_column}{starting_row}:{alpha_column}{ending_row})"
    SUM_RANGE_ON_SHEET = "+SUM('{sheet}'!{alpha_column}{starting_row}:" +\
                         "'{sheet}'!{alpha_column}{ending_row})"

    ADD_CELL = "+{alpha_column}{row}"
    ADD_CELL_FROM_SHEET = "+'{sheet}'!{alpha_column}{row}"
    ADD_COORDINATES = "+{coordinates}"

    LINK_TO_CELL_ON_SHEET = "='{sheet}'!{alpha_column}{row}"
    LINK_TO_COORDINATES = "={coordinates}"

    HLOOKUP = "=HLOOKUP({ref_coords},{start_coords}:{end_coords},{ref_row}" \
              ",FALSE)"

    # LIFE

    COMPUTE_AGE_IN_DAYS = "=IF({birth}, {ref_date}-{birth})"
    COMPUTE_AGE_IN_PERCENT = "=IF({span}, ROUND({age}/{span}*100,0))"
    COMPUTE_SPAN_IN_DAYS = "=IF({death}, {death}-{birth})"

    IS_ALIVE = "=IF(AND({birth}<={ref_date},{ref_date}<{death}),TRUE,FALSE)"

    REPORT_DELTA = "={actual}-{forecast}"
    REPORT_DIFF = '=IFERROR(({actual}-{forecast})/{forecast}, "{placeholder}")'