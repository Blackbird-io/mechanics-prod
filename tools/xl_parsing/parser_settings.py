# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
"""

This module contains settings and functions used for xl_parser

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a
====================  ==========================================================
"""




# Imports
#built-in modules only
from datetime import date




HEADER_ROW = 1

# Possible tab names for BB Metadata
BB_METADATA_NAMES = [
    "bb_metadata",
    "bb metadata",
    "bb_meta",
    "bb meta",
]

# Valid strings that can be input in to the REPORT column for intake upload
VALID_REPORTS = [
    "kpi",
    "covenants",
    "financials",
    "overall",
]

ROLLING_SUM_KEYS = {
    "source",
    "statement",
    "horizon",
    "operation"
}

ALLOWABLE_XL_TEXT = [
    "EBITDA<0",
    "EBITDA<=0",
    "Net Debt<=0",
    "Net Debt<0",
    "Debt<0",
    "Debt<=0",
    "Overperforming",
    "Performing",
    "Needs Review",
]