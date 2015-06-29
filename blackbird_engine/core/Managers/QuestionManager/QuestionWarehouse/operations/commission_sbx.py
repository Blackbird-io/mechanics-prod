#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Operations.commission_sbx
"""

Module defines a question about standard commission on subscription revenues. 
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
name = "commission on subscription revenues?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "% of subscription revenue"
comment = "You should provide a number net of all incentives (SPIFs, prizes, etc.)."
input_type = "number"
input_sub_type = "percent"
bp = "What percent of your subscription revenues go to commission and other incentives?"
basic_prompt = bp
custom_prompt = None
short = "Commission"
transcribe = True
active_elements = 1

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = dict()
element_0["r_max"] = 100
element_0["r_min"] = 0
element_0["shadow"] = 8

element_details = [element_0]
