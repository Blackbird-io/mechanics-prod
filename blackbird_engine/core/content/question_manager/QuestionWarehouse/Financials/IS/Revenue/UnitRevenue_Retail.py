#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Fianncials.IS.Revenue.UnitRevenue_Retail
"""

Retail-specific question about annual revenue for a mature business unit.

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
name = "annual revenue at mature stores?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "Revenue (sales) per year"
comment = None
input_type = "number"
input_sub_type = "currency"
bp = "How much revenue does your average store generate per year at maturity?"
basic_prompt = bp
#
cp = ""
cp += "What are annual sales at your average store {years_to_maturity} years"
cp += "after opening?"
custom_prompt = cp
#
short = "Annual Sales"
transcribe = True
active_elements = 1

