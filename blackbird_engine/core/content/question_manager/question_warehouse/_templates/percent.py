#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: question_warehouse._templates.number
"""

Template for a size-1 number question. 
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
name = "What percent of your life do you spend thinking about blenders?"
question_author = "Sue Knuth"

#Engine parameters
requiredTags = []
optionalTags = []

#Portal parameters
array_caption = None
comment = "Be honest. Everyone thinks about them sometimes."
input_type = "number"
input_sub_type = "percent"
bp = "What percent of your average day do you spend thinking about blenders?"
basic_prompt = bp
custom_prompt = None
short = "Blender attention."
transcribe = True
active_elements = 1        
