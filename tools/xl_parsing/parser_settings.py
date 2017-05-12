# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2017
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




# HEADER_ROW = 1

# Possible tab names for BB Metadata
# This will be the Excel tab that xl_parser will operate on
# Strings are lowercase to support caseless matching
BB_METADATA_NAMES = [
    "_bb_metadata",
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
    "business summary",
]

ROLLING_SUM_KEYS = {
    "source",
    "statement",
    "horizon",
    "operation"
}

CUSTOM_STATUS_KEYS = {
    "source",
    "benchmark",
    "comparison",
    "style"
}

COVENANT_STATUS_KEYS = {
    # "source",
    # "benchmark",
    "comparison",
    "current",
    "limit",
    # "type",
}

ACTION_TO_FORMULA_MAP = {
    "rolling sum over time": "rolling sum over time.",
    "covenant status": "covenant status.",
    "custom status": "custom status.",
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

STATEMENT = "STATEMENT"
LINE_TITLE = "LINE_TITLE"
LINE_NAME = "LINE_NAME"
PARENT_NAME = "LINE_PARENT_NAME"
COMPARISON = "COMPARISON"
SUM_DETAILS = "SUM_DETAILS"
REPORT = "REPORT"
MONITOR = "MONITOR"
PARSE_FORMULA = "PARSE_FORMULA"
ADD_TO_PATH = ("ADD_TO_PATH", "TOPIC_FORMULA")
BEHAVIOR = "BEHAVIOR"
ALERT = ("ALERT", "ALERT_COMMENTARY")
STATUS = "STATUS"
ON_CARD = "ON_CARD"
TAGS = "TAGS"

REQUIRED_COLS = [
    STATEMENT,
    LINE_TITLE,
    LINE_NAME,
    PARENT_NAME,
]