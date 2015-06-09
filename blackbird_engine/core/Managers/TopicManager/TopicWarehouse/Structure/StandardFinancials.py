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




#imports
from DataStructures.Modelling.Financials import Financials
from DataStructures.Modelling.LineItem import LineItem

#globals
knowledge_content = True

#standard financials
standard_financials = Financials()
standard_financials.buildDictionaries()
revenue = LineItem("Revenue")
revenue.tag("GAAP","Operations")
cogs = LineItem("Cost")
cogs.tag("GAAP","Operations","COGS","excludes d&a")
opex = LineItem("Operating Expense")
opex.tag("GAAP","Operations","excludes d&a")
sga = LineItem("SG&A")
sga.tag("GAAP","Operations","excludes d&a")
ebitda = LineItem("EBITDA")
ebitda.tag("Operations")
income_lines = [revenue,cogs,opex,sga,ebitda]
for L in income_lines:
    L.setPartOf(standard_financials)
i_end_is = standard_financials.indexByName("|bb|end Income Statement")
for L in income_lines[::-1]:
    standard_financials.insert(i_end_is,L)
    #insert last one first so can keep using same index
