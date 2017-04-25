# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2017
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: Sheet Map

"""

Module defines the SheetMap class. SheetMap objects stores column
index locations for the xl_parser
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SheetMap         storage for column indexes
====================  ==========================================================
"""




#imports




#globals
#n/a

#classes
class SheetMap():
    """

    SheetMap stores column index locations for the xl_parser module
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    STATEMENT_COL         int, column index
    LINE_TITLE_COL        int, column index
    LINE_NAME_COL         int, column index  
    PARENT_NAME_COL       int, column index
    COMPARISON_COL        int, column index  
    SUM_DETAILS_COL       int, column index
    REPORT_COL            int, column index
    MONITOR_COL           int, column index  
    PARSE_FORMULA_COL     int, column index
    ADD_TO_PATH_COL       int, column index
    BEHAVIOR_COL          int, column index
    ALERT_COMMENTARY_COL  int, column index
    STATUS_COL            int, column index  
    ON_CARD_COL           int, column index
    TAGS_COL              int, column index  
    FIRST_PERIOD_COL      int, column index           

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        self.STATEMENT_COL = None
        self.LINE_TITLE_COL = None
        self.LINE_NAME_COL = None
        self.PARENT_NAME_COL = None
        self.COMPARISON_COL = None
        self.SUM_DETAILS_COL = None
        self.REPORT_COL = None
        self.MONITOR_COL = None
        self.PARSE_FORMULA_COL = None
        self.ADD_TO_PATH_COL = None
        self.BEHAVIOR_COL = None
        self.ALERT_COMMENTARY_COL = None
        self.STATUS_COL = None
        self.ON_CARD_COL = None
        self.TAGS_COL = None
        self.FIRST_PERIOD_COL = None  # First column with a period date and line values

        self.DATES_ROW = 1
        self.TIMELINE_ROW = 2  # "Actual" or "Forecast"
        self.FIRST_ROW = 3  # First row with LineItem data
