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
from . import parser_settings as ps



#globals
#n/a

#classes
class SheetMap():
    """

    SheetMap stores row and column index locations for the xl_parser module
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    cols                  dict() {column name: column index}
    rows                  dict() {row name: row index}
    
    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        self.cols = dict()
        self.rows = dict()

        self.cols[ps.STATEMENT] = None
        self.cols[ps.LINE_TITLE] = None
        self.cols[ps.LINE_NAME] = None
        self.cols[ps.PARENT_NAME] = None
        self.cols[ps.COMPARISON] = None
        self.cols[ps.SUM_DETAILS] = None
        self.cols[ps.REPORT] = None
        self.cols[ps.MONITOR] = None
        self.cols[ps.PARSE_FORMULA] = None
        self.cols[ps.ADD_TO_PATH[0]] = None
        self.cols[ps.BEHAVIOR] = None
        self.cols[ps.ALERT[0]] = None
        self.cols[ps.STATUS] = None
        self.cols[ps.ON_CARD] = None
        self.cols[ps.TAGS] = None
        self.cols["FIRST_PERIOD"] = None   # First column with a period date

        self.rows["DATES"] = 1
        self.rows["TIMELINE"] = 2  # "Actual" or "Forecast"
        self.rows["FIRST_DATA"] = 3  # First row with LineItem data
