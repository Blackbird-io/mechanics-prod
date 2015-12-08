#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.statement_bundle
"""

Module defines StatementBundle, a customized Bundle for Statements. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
StatementBundle       a bundle of statements with a minimal shared interface.
====================  ==========================================================
"""




# Imports
from .bundle import Bundle




# Constants
# n/a

# Classes
class StatementBundle(Bundle):
    """

    A Bundle specifically designed for holding several instances of Statement.
    Includes methods that match the public Statement interface. All methods
    delegate to the Bundle.run_on_all() routine.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    build_tables()        built tables for all defined statements
    reset()               reset all defined statements
    summarize()           summarize all defined statements
    ====================  ======================================================
    """
    def __init__(self):
        pass

    def build_tables(self, *tagsToOmit):
        """


        StatementBundle.build_tables() -> None


        Build tables for each defined statement.
        """
        self.run_on_all("build_tables", *tagsToOmit)
        
    def reset(self):
        """


        StatementBundle.reset() -> None


        Reset each defined statement. 
        """
        self.run_on_all("reset")

    def summarize(self, *tagsToOmit):
        """


        StatementBundle.summarize() -> None


        Summarize each defined statement.
        """
        self.run_on_all("summarize", *tagsToOmit)
    
