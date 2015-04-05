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

Batteries are dictionaries with two keys:
    ``name``           a descriptive string
    ``tests``          a list of test module objects.

Each Test module should provide a consistent interface.
====================  ==========================================================
Test                  Attribute
====================  ==========================================================
result                dict; keys are "testName","output","completed","passed",
                      and "rubric." see Test docs for detail.

do()                  0-argument function, runs test's task script and returns
                      some output
check()               takes output as an argument, checks it against a
                      predefined standard, usually by passing both to a
                      dedicated Grader module
"""




#imports
from . import Basic




#globals
###Define batteries here:
###0
##trial = {}
##trial["name"] = "trial"
##trial["tests"] = [Test_01,Test_02,Test_03]
###1
##validation = {}
##validation["name"] = "validation"
##validation["tests"] = [Test_01,Test_02,Test_03]
