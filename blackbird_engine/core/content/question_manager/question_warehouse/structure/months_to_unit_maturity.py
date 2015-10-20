#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QuestionWarehouse.Structure.MonthsToUnitMaturity
"""

Content module for question. 

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
name = "months to unit maturity?"
question_content = True

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
input_type = "number"
input_sub_type = "months"
basic_prompt = "How quickly does revenue from the unit stabilize?"
custom_prompt = "How many months does it take for revenue from a typical {unit_label_singular} to level out?"
short = "Months to Maturity"
transcribe = True
active_elements = 1
c = ""
c += "A business unit is mature when it's revenue from period to period stays"
c += "\nrelatively constant."
comment = c
