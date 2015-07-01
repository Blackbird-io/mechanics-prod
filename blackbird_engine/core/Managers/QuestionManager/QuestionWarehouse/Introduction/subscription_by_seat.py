#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Introduction.subscription_by_seat
"""

Module defines a binary question about charge per seat. 

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
name = "do you charge subscribers by seat?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "binary"
input_sub_type = None
basic_prompt = "Do you charge subscribers by seat?"
custom_prompt = "Does {company_name} charge subscribers by seat?"
short = "Pricing model"
transcribe = True
active_elements = 1

element_0 = {"toggle_caption_false" : "No (flat subscription fee)",
             "toggle_caption_true" : "Yes (charge by seat)"}

element_details = [element_0]
