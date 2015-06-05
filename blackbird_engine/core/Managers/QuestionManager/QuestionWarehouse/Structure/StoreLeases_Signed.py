#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.NewStoreLeasesNumber
"""

A template for question content modules. Includes all parameters available for
customization. Content modules should not import modules or create any routines
or classes.

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
name = "number of signed new store leases?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "Number"
input_sub_type = None
basic_prompt = "Do you have any leases signed for new stores?"
custom_prompt = None
short = None
transcribe = False
active_elements = 1

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
show_if_rule = {"toggle_caption_true" : "Yes",
                "toggle_caption_false" : "No"}


#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "Number of signed leases:",
             "r_min" : 0,
             "r_max" : 500,
             "r_steps" : 500,
             "shadow" : 2} 
element_details = [element_0]
        
