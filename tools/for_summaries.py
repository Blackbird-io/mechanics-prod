# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2017
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Engine
# Module: tools.for_summaries
"""

Module includes convenience functions for summaries.
====================         ===================================================
Attribute                    Description
====================         ===================================================

DATA:
n/a

FUNCTIONS:
get_line_summary_dict()      generates the Portal-friendly line summary

CLASSES:
n/a
====================         ===================================================
"""




# imports
from datetime import date




# Functions
def get_line_summary_dict(line):
    """


    get_line_summary_dict() -> dict


    --``line`` is an instance of LineItem


    Function produces a dictionary containing summary information for Portal.
    The dictionary will have the following keys:
    "name" -> str
    "value" -> any base type
    "fixed length" -> bool
    "format" -> string in ("string", "decimal", "integer", "date", "ratio",
    "percent")
    """
    row_dict = dict()
    row_dict['name'] = line.title
    row_dict['value'] = line.value
    row_dict['fixed length'] = False
    row_dict['format'] = 'string'

    num_format = line.xl_format.number_format or ""
    val = line.value

    if isinstance(val, str):
        row_dict['format'] = 'string'
    elif '%' in num_format:
        row_dict['format'] = 'percent'
    elif 'x' in num_format or 'ratio' in line.name.split(' '):
        row_dict['format'] = 'ratio'
        print(num_format)
        print(line.title)
        print(line.name)
    elif isinstance(line.value, date):
        row_dict['format'] = 'date'
    elif '$' in num_format:
        row_dict['format'] = 'currency'
        if '.' in num_format:
            row_dict['fixed length'] = True
    elif '$' not in num_format:
        if '.' in num_format:
            row_dict['format'] = 'decimal'
        else:
            row_dict['format'] = 'integer'

    return row_dict
