#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Financials.IS.OperatingExpense.Marketing.WholeMarketingSpendLTM
"""

Asks question about LTM marketing spend at the company as a whole. 

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
name = "ltm whole company marketing spend?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "Here, we are looking to understand the company as a whole."
input_type = "number"
input_sub_type = "currency"
basic_prompt = "In the last 12 months, how much did you spend on marketing?"
custom_prompt = None
short = "LTM Marketing"
transcribe = True
active_elements = 1

