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
from data_structures.modelling.statement import Statement
from data_structures.modelling.new_financials import Financials
from data_structures.modelling.line_item import LineItem




#globals
knowledge_content = True

#standard financials
standard_financials = Financials()

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
    L.setPartOf(standard_financials.income)
    standard_financials.income.append(L)
    
basic_fins = standard_financials.copy()
b_sga_i = basic_fins.income.indexByName("sg&a")
b_opex_i = basic_fins.income.indexByName("operating expense")
b_sga = basic_fins.income[b_sga_i]
b_opex = basic_fins.income[b_opex_i]
b_sga.setPartOf(b_opex)
