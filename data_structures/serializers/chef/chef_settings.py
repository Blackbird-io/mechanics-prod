# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.chef_settings
"""

This module contains settings and functions used in Chef.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
COMMENT_CUSTOM         bool; whether to include custom comment in cell comments
COMMENT_FORMULA_NAME   bool; whether to include formula names in cell comments
COMMENT_FORMULA_STRING bool; whether to include formula string in cell comments

DEFAULT_SCENARIOS      list; scenarios to automatically include on model

AREA_BORDER            bool; whether to add a border around sheet Areas
BLANK_BETWEEN_TOP_LINES bool; whether to include a blank line between top lines
COLUMN_WIDTH           float; Excel column width
PARAM_DECIMAL_POINTS   int; number of decimal points to include for parameters

FUNCTIONS:
n/a

CLASSES:
n/a
====================  =========================================================
"""




# Imports
# n/a




# Constants

# COMMENTS
COMMENT_FORMULA_NAME = True
COMMENT_FORMULA_STRING = True
COMMENT_CUSTOM = True

# SCENARIOS
DEFAULT_SCENARIOS = ["Terrible", "Bad", "Good", "Awesome"]

# FORMATTING
AREA_BORDER = False
BLANK_BETWEEN_TOP_LINES = True
COLUMN_WIDTH = 16.71
PARAM_DECIMAL_POINTS = 2

# TOGGLES
COLLAPSE_ROWS = False
SCENARIO_SELECTORS = False
