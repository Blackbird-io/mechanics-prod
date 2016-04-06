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
name = "How do you feel about whales on several dimensions?"
question_author = "Sue Knuth"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "Quantity of fun:"
comment = None
input_type = "mixed"
input_sub_type = None
bp = "How do you feel about whales?"
basic_prompt = bp
custom_prompt = None
short = "Details Matter"
transcribe = True
active_elements = 3

# Advanced Config I: gating element for conditional questions
#
# **Gating element must be binary.**
#
# User will see the gating element first. If they provide a truthy answer,
# Portal will collect their responses to the remaining elements. Otherwise,
# Portal will send back a length==1 PortalResponse. See API for more details.
#
# Gating element will be active by default.
#
##gating_element = {"main_caption" : "Do you care about details?",
##                "toggle_caption_true" : "Yes",
##                "toggle_caption_false" : "No"}


# Advanced Config II: input element details.
#
# Details are always optional, unless you want to ask a ``mixed``-type question.
# For ``mixed``-type questions, make sure to include the input_type and subtype
# for each element.
#
# Elements will be active by default.
#
element_0 = {"input_type" : "number",
             "main_caption" : "small whales",
             "r_min" : 0,
             "r_max" : 100,
             "r_steps" : 10,
             "shadow" : 20}

element_1 = {"input_type" : "number",
             "main_caption" : "very small whales",
             #the best kind of whale!
             "r_min" : 0,
             "r_max" : 100,
             "r_steps" : 10,
             "shadow" : 50}

element_2 = {"input_type" : "date",
             "main_caption" : "first time you saw a whale"}
element_3 = {"input_type" : "date",
             "main_caption" : "last time you saw a whale"}

element_details = [element_0,
                   element_1,
                   element_2,
                   element_3]
        
