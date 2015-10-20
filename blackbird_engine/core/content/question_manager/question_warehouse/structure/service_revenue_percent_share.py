#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: question_warehouse.structure.service_rev_percent_share
"""

Question asks user to specify the percentage of their revenue that comes from
products, as opposed to services.
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
name = "Percent of revenue from services?"
question_author = "Ilya Podolyako"

#Engine parameters
requiredTags = []
optionalTags = []

#Portal parameters
array_caption = None
comment = "We are going to assume that the remainder comes from sale of goods."
input_type = "number"
input_sub_type = None
#
bp = "What percentage of ?"
basic_prompt = bp
#
cp = "Approximately what percent of {company_name} revenue comes from sale of"
cp += " services?"
custom_prompt = cp
#
short = "Service Percentage."
transcribe = True
active_elements = 1        


#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
element_0 = {"shadow" : 50}

element_details = [element_0]
