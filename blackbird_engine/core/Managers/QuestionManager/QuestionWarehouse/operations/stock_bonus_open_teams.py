#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Operations.stock_bonus_open_teams
"""

Module defines a question about stock bonuses across 5 teams. Module does
**not** list the actual team names. Topics should fill those in as necessary on
their own. 
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
name = "annual stock bonus as percent of salary for open teams?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "% of average salary"
comment = "``Equity`` includes stocks, options, warrants, profit shares, and other"
comment += " units that represent partial ownership of the company's earnings."
input_type = "number"
input_sub_type = "percent"
bp = "How much equity do your teams receive annually, as a percent of their salary?"
basic_prompt = bp
custom_prompt = "How much equity do teams at {company_name} receive annually,"
custom_prompt += " as a percent of their salary?"
short = "Incentive compensation (equity)"
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
