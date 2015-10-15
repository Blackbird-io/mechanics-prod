#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.FutureStoreCount_3yrs
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
name = "store count over next 3 years?"
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
basic_prompt = "How many total stores do you expect to have open on Dec. 31 of the next 3 years?"
custom_prompt = None
short = "Store Openings"
transcribe = True
active_elements = 3

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "December 31, 2016",
             "r_min" : 0,
             "r_max" : 500,
             "r_steps" : 500}
element_0 = {"main_caption" : "December 31, 2017",
             "r_min" : 0,
             "r_max" : 500,
             "r_steps" : 500}
element_0 = {"main_caption" : "December 31, 2018",
             "r_min" : 0,
             "r_max" : 500,
             "r_steps" : 500}

element_details = [element_0,
                   element_1,
                   element_2]
        
