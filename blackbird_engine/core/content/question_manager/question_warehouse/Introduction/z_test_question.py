#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Introduction.test_question
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
name = "Does new conditional functionality work?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "Let's check this out."
comment = None
input_type = "mixed"
input_sub_type = None
bp = "Does new conditional functionality work?"
basic_prompt = bp
custom_prompt = "Does new conditional functionality work for {company_name}?"
short = "Condo"
transcribe = True
active_elements = 2

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
gating_element = {"main_caption" : "Does this work?",
                  "toggle_caption_true" : "Yes",
                  "toggle_caption_false" : "No"}

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "How well?",
             "r_min" : 0,
             "r_max" : 100,
             "r_steps" : 10,
             "input_type" : "number"} 
element_1 = {"main_caption" : "How much do you like it?",
             "input_type" : "number"}
element_2 = {"main_caption" : "Is this awesome?",
             "input_type": "binary"}
element_3 = {"main_caption" : "When we eat cake",
             "input_type" : "date"}

element_details = [element_0,
                   element_1,
                   element_2,
                   element_3]
        
