#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.QuestionTemplate_Detailed
"""

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
name = "Is this a detailed question template? What are the details?"
question_author = "Sue Knuth"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "What are the details that matter to you?"
comment = None
input_type = "Text"
input_sub_type = None
bp = "Do you care about details?"
basic_prompt = bp
custom_prompt = None
short = "Details Matter"
transcribe = True
active_elements = 3

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
show_if_rule = {"main_caption" : "Do you care about details?",
                "toggle_caption_true" : "Yes",
                "toggle_caption_false" : "No"}

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "First Detail"}
element_1 = {"main_caption" : "Second Detail"}
element_2 = {"main_caption" : "Third Detail"}

element_details = [element_0,
                   element_1,
                   element_2]
        
