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
import os




# Constants

# COMMENTS
COMMENT_FORMULA_NAME = True
COMMENT_FORMULA_STRING = True
COMMENT_CUSTOM = True

# SCENARIOS
DEFAULT_SCENARIOS = ["Terrible", "Bad", "Good", "Awesome"]

# FORMATTING
AREA_BORDER = False
BLANK_BETWEEN_TOP_LINES = False
COLUMN_WIDTH = 16.71
PARAM_DECIMAL_POINTS = 2

# TOGGLES
COLLAPSE_ROWS = False
SCENARIO_SELECTORS = False
FILTER_PARAMETERS = False

# DEFAULT TEXT

# annual summary page
SUMMARY_TITLE = "Annual Summary"
COMPLETE_LABEL = "Complete Summary Period:"
AVAILABLE_LABEL = "Available Months:"

# cover sheet
COVER_TITLE = "Cover"
DATE_LABEL = 'Model Date:'
QCOUNT_LABEL = 'Conversation Length:'
ESTIMATED_LABEL = 'ESTIMATED VALUES'
DISCLAIMER_TEXT = 'Blackbird uses classic value analysis coupled with proprietary software to estimate the financial performance of each business member. In certain cases, Blackbird software may make assumptions about a company that turn out to be False. You should carefully check each of these numbers prior to entering into any transaction.'
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'static', 'blackbird_engine_2X_410x120.png')

# tab colors
SCENARIO_TAB_COLOR = '4f81bd'
SUMMARY_TAB_COLOR = '000000'
VALUATION_TAB_COLOR = '556a2c'
COVER_TAB_COLOR = 'ffffff'
TIMELINE_TAB_COLOR = 'cccccc'

