#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.TimeToLease
"""

Module asks question about time to find the right property and lease a store.

See Blackbird Portal-Engine API Guide for attribute explanations.
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
name = "time to sign a new store lease?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "If tomorrow you decided to open a new store, you would need
comment += "this many months to find the right property and get all the "
comment += "paperwork in order."
input_type = "number"
input_sub_type = "months"
basic_prompt = "How many months do you usually spend looking before you sign"
basic_prompt += " a new store lease?"
custom_prompt = None
short = "Property Search"
transcribe = True
active_elements = 1

