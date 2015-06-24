#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Financials.ID.OperatingExpense.Labor.UnitEmployeeExpense
"""

A question about unit employee expense. 

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
name = "unit employee expense per year?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "Employee expense includes salary, bonuses, benefits, unemployment"
comment += " insurance, and taxes." 
input_type = "number"
input_sub_type = "currency"
basic_prompt = "What is the annual employee expense for a given unit?"
cp = "What is the annual employee expense for a {unit_label_singular}?"
custom_prompt = cp
short = "Employee Expense"
transcribe = True
active_elements = 1

