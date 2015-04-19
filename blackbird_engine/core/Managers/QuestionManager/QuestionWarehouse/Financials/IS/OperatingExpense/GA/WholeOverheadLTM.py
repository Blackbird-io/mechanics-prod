#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QuestionWarehouse.Financials.IS.OperatingExpense.GA.WholeOverheadLTM
"""

Content module for question about whole company overhead (excluding marketing)
over the last 12 months. 

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
name = "LTM whole company overhead, excluding marketing?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "G&A, excluding marketing:"
comment = None
input_type = "number"
input_sub_type = "currency"
basic_prompt = "In the last 12 months, what did you spend on company overhead?"
custom_prompt = None
short = None
transcribe = False
active_elements = 1

