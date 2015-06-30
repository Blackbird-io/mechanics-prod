#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Financials.Revenue.seat_price_monthly
"""

Question about monthly seat price (in a subscription environment). 

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
name = "monthly seat price?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "We are looking to understand your"
comment += "net price per month (including any discounts or grace periods you may offer)."
input_type = "number"
input_sub_type = "currency"
basic_prompt = "What's your monthly charge per seat?"
custom_prompt = None
short = "Seat Price"
transcribe = True
active_elements = 1

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"r_max" : 50000,
             "shadow" : 500}
element_details = [element_0]

