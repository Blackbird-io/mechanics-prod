#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.QuestionManager.QuestionWarehouse.QuestionTemplate
"""

Cpntent module for question. 

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
name = "unit lifespan in years?"
question_content = True

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
input_type = "number"
input_sub_type = "years"
basic_prompt = "For how many years does a typical unit stay active"
custom_prompt = "For how many years does a typical {unit_label_singular} operate?"
short = "Unit Life (Yrs)"
transcribe = True
active_elements = 1
c = ""
c += "Our goal is to get a sense of how the foundation of your business evolves"
c += "\nover time. The lifecycle of a business unit is the time between when it"
c += "\nstarts operating and when it stops producing revenue."
comment = c
