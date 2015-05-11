#SharedKnowledge
"""

Repository for general knowledge about business units and company structure. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
unit_life_spans       
unit_names
unit_number_limit

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""
knowledge_content = True

unit_life_spans = dict()
unit_life_spans["longest"] = 30
unit_life_spans["retail"] = 8
unit_life_spans["default"] = 5

unit_labels = dict()
unit_labels["retail"] = {"singular": "store", "plural" : "stores"}

unit_number_limit = 500
#max number of units in a model

unit_months_to_mature = dict()
unit_months_to_mature["default"] = unit_months_to_mature[None] = 12
unit_months_to_mature["retail"] = 30

months_to_first_unit = dict()
months_to_first_unit["default"] = 14
months_to_first_unit["retail"] = 10
