#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.SubscriberLifeRange
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
name = "customer life range?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "Think of a range that would cover 95 out of 100 cases."
input_type = "number-range"
input_sub_type = "months"
basic_prompt = "How long do most customers keep their subscription?"
custom_prompt = "How long do most customers keep their subscription to {product_name}?"
short = "Subscriber Life Range"
transcribe = True
active_elements = 1

