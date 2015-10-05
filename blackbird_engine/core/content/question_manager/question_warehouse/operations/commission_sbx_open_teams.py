#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Operations.sbx_commission_open_teams
"""

Module defines a question about commission on subscription revenues for up to
5 teams. Module does **not** list the actual team names. Topics should fill
those in as necessary on their own. 
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
name = "commission on subscription revenues for open teams?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "% of subscription revenue"
comment = None
input_type = "number"
input_sub_type = "percent"
bp = "How much commission do your teams earn on subscription revenue?" 
basic_prompt = bp
custom_prompt = "How much commission do your teams earn on revenue from"
custom_prompt += " {product_name} subscriptions?"
short = "Receipts after commission"
transcribe = True
active_elements = 1

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
#n/a
