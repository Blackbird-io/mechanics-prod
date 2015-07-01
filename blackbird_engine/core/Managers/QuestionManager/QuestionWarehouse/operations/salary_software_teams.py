#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Operations.EmployeeCount_Software
"""

Module defines a question about average salaries for teams common to a software
organization. Question includes a catch-call "Everyone else" category.
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
name = "average annual salary across software organization?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "We think of salary as the baseline cash compensation, excluding any bonus payments. "
input_type = "number"
input_sub_type = "currency"
bp = "What annual salary do your employees earn, on average?"
basic_prompt = bp
custom_prompt = None
short = "Salaries"
transcribe = True
active_elements = 4

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "development"}
element_1 = {"main_caption" : "sales"}
element_2 = {"main_caption" : "management"}
element_3 = {"main_caption" : "everyone else"}

element_details = [element_0,
                   element_1,
                   element_2,
                   element_3]
        
