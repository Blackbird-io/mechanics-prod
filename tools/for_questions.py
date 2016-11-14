# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: tools.for_printing

"""

Module provides functions for formatting MiniQuestions in Topic.scenario_2
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
format_statement_as_table()      format data into a ``name...value`` line
format_completed()    format as line with a completed indicator

CLASSES:
n/a
====================  ==========================================================
"""




from data_structures.modelling.line_item import LineItem
from data_structures.modelling.link import Link
from data_structures.modelling.statement import Statement




def format_statement_as_table(statement, mini_question):
    """


    format_statement_as_table() -> MiniQuestion


    Function takes a Statement, and formats a Table Style - MiniQuestion which
    will have input rows based on each line in the statement. Lines with details
    will be ignored as only the lowest level detail lines will have input rows.

    Mini_question must have a column called "Line"
    Can optionally have a column called "Forecast" which will display statement
    line values.
    """

    fixed_line_names = []
    proj_values = []
    for line in statement.get_full_ordered():
        if line._details:
            # Skip
            continue
        else:
            fixed_line_names.append(line.title)
            proj_values.append("{:,.2f}".format(line.value))

    for elem in mini_question.input_array:
        if elem.main_caption == 'Line':
            elem.fixed_rows = fixed_line_names
        if elem.main_caption == 'Forecast':
            elem.fixed_rows = proj_values
