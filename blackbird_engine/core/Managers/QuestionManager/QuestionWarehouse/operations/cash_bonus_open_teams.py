#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: QW.Operations.cash_bonus_open_teams
"""

Module defines a question about cash bonuses across 5 teams. Module does **not**
list the actual team names. Topics should fill those in as necessary on their
own. 
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
name = "annual cash bonus as percent of salary for open teams?"
question_author = "Ilya Podolyako"

#Engine parameters
#
requiredTags = []
optionalTags = []

#Portal parameters
#
array_caption = "% of average salary"
comment = "cash bonuses and incentive compensation only."
input_type = "number"
input_sub_type = "percent"
bp = "How much do your teams earn in annual cash bonuses, as a percent of their salary?"
basic_prompt = bp
custom_prompt = "How much do teams at {company_name} earn in annual cash bonuses, as a percent of their salary?"
short = "Incentive Compensation (cash)"
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
