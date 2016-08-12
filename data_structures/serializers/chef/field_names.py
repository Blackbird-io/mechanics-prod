# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.field_names
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
FieldNames            standard keys for column and row lookups
====================  =========================================================
"""




# Imports
# n/a




# Constants
# n/a

# Module Globals
# n/a

# Classes
class FieldNames:
    """

    Class stores standard keys for row and column lookups within SheetData. 
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    BASE_CASE             "base_case"
    CUSTOM_CASE           "custom_case"

    LABELS                "labels"
    MASTER                "master"
    VALUES                "values"

    REF_DATE              "ref_date"
    AGE                   "age"
    ALIVE                 "alive"
    SPAN                  "span"
    PERCENT               "percent"

    FUNCTIONS:
    n/a
    ====================  =====================================================
    """
    # GENERAL
    
    LABELS = "labels"
    MASTER = "master"
    VALUES = "values"
    TITLE = "title"

    # SCENARIOS
    SELECTOR = "selector"

    ACTIVE_SCENARIO = "active_scenario"
    BASE_CASE = "base_case"
    CUSTOM_CASE = "custom_case"

    IN_EFFECT = 'Active'
    CUSTOM = "Custom"
    BASE = "Base"

    # LIFE

    REF_DATE = "ref_date"
    START_DATE = "period_start"
    AGE = "age"
    ALIVE = "alive"
    SPAN = "span"
    PERCENT = "percent"

    # STANDARD AREAS
    TIMELINE = "time_line"
    PARAMETERS = "parameters"
    GENERAL = "general"
    SIZE = "size"

    # other lables
    SIZE_LABEL = "store count"
