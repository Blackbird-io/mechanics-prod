#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.TimeToBuildStore
"""

Module asks question about time to find the right property and lease a store. 
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
name = "time to open leased store?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "The pre-opening period covers all construction, permitting, hiring, "
comment += "and marketing activities necessary for the doors to open. You "
comment += "should include a bit of cushion (think of when you can reasonably"
comment += "promise to deliver a store)."
input_type = "number"
input_sub_type = "months"
basic_prompt = "Once you sign a lease, how many months do you usually need to"
basic_prompt += "open a new store for business?"
custom_prompt = None
short = "Pre-Opening"
transcribe = True
active_elements = 1

