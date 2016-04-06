#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.sytem.print_as_line
"""

Module defines the PrintAsLine class, which prints objects as a line when mixed
in. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
PrintAsLine           mix-in class, supports ``[name].....[value]`` prints
====================  ==========================================================
"""




#imports
import tools.for_printing as printing_tools




#globals
#n/a

#classes
class PrintAsLine:
    """
    Mix-in class. Instances return a well-formatted line for on str() calls. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    formatted             ``[name] ... [value]`` string for pretty printing
    
    FUNCTIONS:
    __str__()             return copy of ``formatted``, then clear the attr
    pre_format()          format instance as line using printing tools
    ====================  ======================================================
    """
    def __init__(self):
        self.formatted = None

    def __str__(self):
        """


        PrintAsLine.__str__() -> str


        Checks if object is already formatted. Allows callers to format first,
        print later. Clears formatted string after every call to make sure
        value is fresh. 
        """
        if not self.formatted:
            self.pre_format()
        result = self.formatted[:]
        self.formatted = None
        #
        return result

    def pre_format(self, **kargs):
        """


        PrintAsLine.pre_format(**kargs) -> None


        Method formats instance for display. Method delegates all work to
        printing_tools.format_as_line(). Method stores that function's
        output at instance.formatted.
        """
        self.formatted = printing_tools.format_as_line(self, **kargs)
    

