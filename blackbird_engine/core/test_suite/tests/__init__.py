#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.__init__

"""
The Tests package contains both individual tests and pre-made batteries of those
tests. The batteries allow higher level modules to perform different types of
analysis without manually assembling lists of attributes for this module.

Each Test module should provide a consistent interface.
====================  ==========================================================
Test                  Attribute
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a
====================  ==========================================================
"""




#imports
from . import basic
from . import legacy
from . import stateful
from . import templates




#globals
#n/a
