#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.QuestionManager.QuestionWarehouse.QuestionTemplate
"""

A template for question content modules. Includes all parameters available for
customization. Content modules should not import modules or create any routines
or classes.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
active_elements
array_caption
basic_prompt
comment
custom_prompt
input_type
input_sub_type
name
optionalTags
question_content
requiredTags
short
transcribe

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""
question_content = True
name = "did we fix the bool response processing?"
question_author = "Sue Knuth"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "bool"
input_sub_type = None
basic_prompt = "All that shimmers is gold."
custom_prompt = None
short = None
transcribe = True
active_elements = 1

