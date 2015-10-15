#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.FirstStore
"""

A question specifically about stores.

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
name = "latest store open date?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
c = "You can approximate the date if you'd like. We are trying to understand"
c += "how your company has grown over time, so the month and year matter most."
comment = c
input_type = "date"
input_sub_type = None
basic_prompt = "When did you open your most recent store?"
custom_prompt = None
short = "Most Recent Store"
transcribe = True
active_elements = 1

