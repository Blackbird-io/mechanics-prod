#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QuestionWarehouse.Overview.CompanyIndustry
"""

"What industry are you in?"

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

name = "company industry?"
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
basic_prompt = "What industry are you in?"
custom_prompt = None
short = "Industry"
transcribe = True
user_can_add = False
active_elements = 1

