#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: question_warehouse.structure
"""

Question about source of company revenue. 
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
name = "does revenue come from sale of goods or services?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = None
comment = None
input_type = "bool"
input_sub_type = None
basic_prompt = "Do you sell goods or services?"
custom_prompt = "Does {company_name} sell goods or services?"
short = "Revenue profile"
transcribe = True
active_elements = 2

#Advanced Configuration: input element details.
#See Blackbird Engine API for parameters available with each question type. 
#
element_0 = {"main_caption" : "Goods"}
element_1 = {"main_caption" : "Services"}

element_details = [element_0,
                   element_1]
        
