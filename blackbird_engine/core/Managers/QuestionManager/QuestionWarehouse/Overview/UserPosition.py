#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QuestionWarehouse.Overview.UserPosition
"""
"What is your position in the company?"

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
user_can_add

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""

name = "user position?"
question_content = True
#
#Engine
requiredTags = []
optionalTags = []
#
#Portal
array_caption = None
comment = None
input_type = "text"
input_sub_type = None
basic_prompt = "What is your position in the company?"
custom_prompt = "What is your role at {company_name}?"
short = "role"
transcribe = True
user_can_add = False
active_elements = 1

