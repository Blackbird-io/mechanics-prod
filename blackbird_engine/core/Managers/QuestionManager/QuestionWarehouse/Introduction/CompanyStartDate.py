#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Overview.StartDate
"""

A question about when the company was founded. 

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
name = "company start date?"
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
basic_prompt = "When did the company start operating?"
custom_prompt = "When did {company_name} start operating?"
short = "Est."
transcribe = True
active_elements = 1

