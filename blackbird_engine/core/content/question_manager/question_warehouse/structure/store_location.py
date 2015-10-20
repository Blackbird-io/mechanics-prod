#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.StoreLocation
"""

A question specifically about stores.

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
name = "store location?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
c = "Every store is unique."
comment = c
input_type = "text"
input_sub_type = None
basic_prompt = "Where was the store located?"
custom_prompt = "Where was your {identifier} store located?"
short = "Store Location"
transcribe = False
active_elements = 4

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "Address", "shadow" :  "1220 W. 19th Street"}
element_1 = {"main_caption" : "City", "shadow" : "Houston"}
element_2 = {"main_caption" : "State", "shadow" : "TX"}
element_3 = {"main_caption" : "Neighborhood", "shadow" : "The Heights"}
element_details = [element_0,
                   element_1,
                   element_2,
                   element_3]
        
#Advanced Configuration: show_if rule.
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a
