#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Financials.Revenue.SubscriptionPrice_Monthly
"""

Question about monthly subscription price. 

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
name = "monthly subscription price?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "We are looking to understand the "
comment += "net price per month (including any discounts or grace periods you may offer)."
input_type = "number"
input_sub_type = "currency"
basic_prompt = "What's the monthly price of your subscription for an average customer?"
custom_prompt = "How much does an average customer pay per month to subscribe to {product_name}?"
short = "Subscription Price"
transcribe = True
active_elements = 1

