#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Financials.IS.Revenue.UnitRevenue_Generic
"""

A question about generic unit revenue. 
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
name = "annual unit revenue at maturity?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "number"
input_sub_type = "currency"
basic_prompt = "How much annual revenue does your average unit generate at maturity?"
#
cp = ""
cp += "How much annual revenue does your average {unit_label_singular} generate"
cp += "after {years_to_maturity} years?"
custom_prompt = cp
#
short = "Annual Sales"
transcribe = True
active_elements = 1

