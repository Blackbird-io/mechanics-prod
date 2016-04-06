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
##element_0 = {"main_caption" : "First Detail"}
##element_1 = {"main_caption" : "Second Detail"}
##element_2 = {"main_caption" : "Third Detail"}
##
##element_details = [element_0,
##                   element_1,
##                   element_2]
        
