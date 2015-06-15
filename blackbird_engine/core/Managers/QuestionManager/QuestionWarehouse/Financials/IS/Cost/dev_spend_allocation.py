#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Fins.IS.cost.dev_spend_allocation
"""

Module defines question about the percentage of development spend the user
allocates to product cost. 
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
name = "percent of dev spend allocated to cost?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "% allocated to cost"
comment = "Feel free to estimate. We are looking to get a better sense of your accounting."
input_type = "number"
input_sub_type = "percent"
bp = "What percentage of your total spending on development do you allocate to product cost?" 
basic_prompt = bp
custom_prompt = None
short = "Cost allocation"
transcribe = True
active_elements = 1

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
#n/a
