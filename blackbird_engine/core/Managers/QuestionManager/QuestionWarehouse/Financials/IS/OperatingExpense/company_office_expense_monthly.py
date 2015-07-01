#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Financials.IS.OperatingExpense.host_spend_monthly
"""

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
name = "monthly office expense for whole company?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "per month"
comment = "You should count all locations where you pay rent together. Include "
comment += "common area, maintenance, utilities, and any other charges that "
comment += "go with the space."
comment += "utilities, janitorial, and other occupancy charges."
input_type = "number"
input_sub_type = "currency"
bp = "What is your total monthly office expense?"
basic_prompt = bp
custom_prompt = None
short = "Occupancy"
transcribe = True
active_elements = 1

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
element_0 = dict()
element_0["r_min"] = 0
element_0["r_max"] = 10000000
#assume no one in our target demo spends more than $10mm per month on offices
element_details = [element_0]
