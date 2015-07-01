#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Introduction.software_license_status
"""

Module defines a binary question about the contract model for software sales. 

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
name = "software subscription or product?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "binary"
input_sub_type = None
basic_prompt = "Do you sell your software as a subscription (term license) or a product (perpetual license)?"
custom_prompt = "Do you sell {product_name} as a subscription (term license) or a product (perpetual license)?"
short = "Distribution model"
transcribe = True
active_elements = 1

element_0 = {"toggle_caption_false" : "product",
             "toggle_caption_true" : "subscription"}

element_details = [element_0]
