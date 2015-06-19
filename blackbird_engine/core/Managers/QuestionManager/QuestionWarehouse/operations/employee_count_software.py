#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Operations.EmployeeCount_Software
"""

Module defines question about head count across teams common to a software
organization. 

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
name = "employee head count across software company roles?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "number"
input_sub_type = None
bp = "How many people work in each of the following areas?"
basic_prompt = bp
custom_prompt = "How many people work in each of the following areas at {company_name}?" 
short = "Team composition"
transcribe = True
active_elements = 4

#Advanced Configuration: show_if
#See Blackbird Engine API for a description of show_if functionality. 
#
#n/a

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "Development"}
element_1 = {"main_caption" : "Sales"}
element_2 = {"main_caption" : "Management"}
element_3 = {"main_caption" : "Everyone else"}

element_details = [element_0,
                   element_1,
                   element_2,
                   element_3]
        
