#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.BusinessSummary
"""

Module defines BusinessSummary class
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BusinessSummary       dictionary with pre-populated fields
====================  ==========================================================
"""




#imports
from ..Guidance.stage import Stage




#globals
mandatory_summary_fields = ["credit_capacity"]

#classes
class BusinessSummary(dict, Stage):
    """

    Class is a daughter of dict, with prepopulated mandatory fields. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a
    
    FUNCTIONS:
    __str__               mildly pretty print
    ====================  ======================================================
    """
    def __init__(self):
        dict.__init__(self)
        Stage.__init__(self)
        self = dict.fromkeys(self, mandatory_summary_fields)
        
    
    def __str__(self, tab = None):
        result = ""
        name_field_width = 25
        dots = 8
        attrs_to_print = sorted(self.keys())
        for attr_name in attrs_to_print:
            attr_val = self[attr_name]
            #may need to add rounding here
            line = "\t" + str(attr_name) + ":"
            line += ((name_field_width - len(attr_name)) + dots) * "."
            line += str(attr_val) + "\n"
            result = result + line
        return result      
