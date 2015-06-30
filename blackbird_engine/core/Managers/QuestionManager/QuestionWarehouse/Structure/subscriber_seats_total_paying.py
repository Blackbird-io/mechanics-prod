#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Structure.subscriber_seats_total_paying
"""

Module asks question about total paying subscriber seats (key revenue driver
when company bases subscription charges per seat).

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
name = "total paying subscriber seats?"

question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = "Total for all subscribers."
input_type = "number"
input_sub_type = None
basic_prompt = "How many paying seats do you have?"
custom_prompt = "How many paying seats make up {company_name}'s subscription revenue?"
short = "Subscriber Seats"
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
             "r_max" : 1000000,
             "shadow" : 275} 
element_details = [element_0]
        
