#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.QuestionManager.QuestionWarehouse.QuestionTemplate_Detailed
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
name = "Is this a template for question_content modules?"
question_author = "Sue Knuth"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "text"
input_sub_type = None
basic_prompt = None
custom_prompt = None
short = None
transcribe = False
active_elements = 1

