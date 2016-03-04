#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: tests.basic.__init__

"""
The tests package contains both individual tests and pre-made batteries of those
tests. The batteries allow higher level modules to perform different types of
analysis without manually assembling lists of attributes for this module.

Each test module should provide a consistent interface.
====================  ==========================================================
Test                  Attribute
====================  ==========================================================

DATA:
batteries             dict; human-readable collection of test batteries by area

FUNCTIONS:
n/a
====================  ==========================================================
"""




#imports
from . import api_forecast
from . import api_interview
from . import api_landscape
from . import ex_01
from . import retail_3
from . import retail_4
from . import software_1
from . import software_2
from . import software_3
from . import software_4
from . import software_5
from . import summarization

# placeholder for new imports




# test batteries
batteries = {}
batteries["software"] = [software_1,
                         software_2,
                         software_3,
                         software_4,
                         software_5]

batteries["retail"] = [retail_3,
                       retail_4]
