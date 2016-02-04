#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.serializers.eggcellent.excel_formulas
"""

Module defines a class that stores string templates for commonly used formulas.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
FormulaTempaltes      string templates with named fields
====================  ==========================================================
"""




# Imports
# n/a




# Constants
# n/a

# Module Globals
# n/a

# Classes
class FormulaTemplates:
    SUM_RANGE = "+SUM({sheet}!{alpha_column}{starting_row}:{sheet}!{alpha_column}{ending_row}"
    ADD_CELL = "+{alpha_column}{row}"
    ADD_CELL_FROM_SHEET = "+{sheet}!{alpha_column}{row}"
    ADD_COORDINATES = "+{coordinates}"

    LINK_TO_CELL_ON_SHEET = "={sheet}!{alpha_column}{row}"
