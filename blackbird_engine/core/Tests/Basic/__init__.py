#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.__init__

"""
The Tests package contains both individual tests and pre-made batteries of those
tests. The batteries allow higher level modules to perform different types of
analysis without manually assembling lists of attributes for this module.

Each Test module should provide a consistent interface.
====================  ==========================================================
Test                  Attribute
====================  ==========================================================

DATA:
result                dict; keys are "testName","output","completed","passed",
                      and "rubric." see Test docs for detail.

FUNCTIONS:
do()                  0-argument function, runs test's task script and returns
                      some output
check()               takes output as an argument, checks it against a
                      predefined standard, usually by passing both to a
                      dedicated Grader module
====================  ==========================================================
"""




#imports
from . import Ex_01
from . import Summarization
from . import API_Forecast
from . import API_Interview
from . import API_Landscape

from . import interview_retail_2_ext
from . import interview_software_0
from . import interview_software_4
