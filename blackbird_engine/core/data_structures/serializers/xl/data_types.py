#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.serializers.eggcellent.data_types
"""

Module defines a class that stores explicit data type codes compatible with the
Excel cell.set_explicit_value(data_type) interface.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
DataTypes             known cell data types
====================  ==========================================================
"""




# Imports
# n/a




# Constants
# n/a

# Module Globals
# n/a

# Classes
class DataTypes:
    """

    Class stores type strings known to the excel interface. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    BOOL                  
    FORMULA               forces Excel to try and interpret string as a formula
    FORMULA_CACHE_STRING

    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    BOOL = "b"
    FORMULA = "f"
    FORMULA_CACHE_STRING = "str"
