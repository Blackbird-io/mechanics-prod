#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.structure.subscription_term
"""

Module asks question about the length of a subscription contract. Includes
input_array details. 

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
name = "subscription term in months?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "The ``term`` is the length of time during which you provide services"
comment = " under the subscription contract. Exclude any options or renewals."
input_type = "number"
input_sub_type = "months"
basic_prompt = "How long is the standard subscription term for your customers?"
custom_prompt = "How long is the standard subscription for {product_name}?"
short = "Subscription Term"
transcribe = True
active_elements = 1

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"r_min" : 0,
             "r_max" : 90,
             "shadow" : 6} 
element_details = [element_0]
        
