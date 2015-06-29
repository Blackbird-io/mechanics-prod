#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Introduction.SharedKnowledge
"""

Module contains standard paths for opening, running, and concluding an interview
about a business. The standard elements provide a starting point. Downstream
topics can refine the path by adding or removing detail. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
structure
revenue
cogs
opex
sga
ebitda
growth
uses
analytics
summarization
#
closing_lines
income_lines

#
standard_open
standard_core
standard_close

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
standard_open = Financials(populate = False)
standard_core = Financials(populate = False)
standard_close = Financials(populate = False)

#1. Build out standard interview opening.
#
structure = LineItem("Structure")
#
structure.tag("Deterministic", field = "req")
structure.guide.priority.increment(3)
structure.guide.quality.setStandards(2,5)
structure.setPartOf(standard_open)
#
standard_open.append(structure)


#2. Build out standard interview core. Downstream topics will likely modify this
#part of the path as they notice characteristics that may be salient about
#a particular business.
#
revenue = LineItem("Revenue")
cogs = LineItem("Cost")
opex = LineItem("Operating Expense")
sga = LineItem("SG&A")
ebitda = LineItem("EBITDA")
#
revenue.tag("GAAP", "Operations")
cogs.tag("GAAP", "Operations", "COGS", "excludes d&a")
opex.tag("GAAP", "Operations", "excludes d&a")
sga.tag("GAAP", "Operations", "excludes d&a")
ebitda.tag("Operations")
#
income_lines = [revenue,
                cogs,
                opex,
                sga,
                ebitda]
for L in income_lines:
    L.setPartOf(standard_core)
    L.guide.priority.increment(3)
    L.guide.quality.setStandards(1,5)
#
standard_core.extend(income_lines)


#3. Build out standard path for concluding the interview.
#
#This piece also includes ``behind-the-scenes`` steps that guide the Engine
#through standard post-interview processing (pricing analysis, summarization).
#
growth = LineItem("growth")
uses = LineItem("uses")
analytics = LineItem("analytics")
summarization = LineItem("summarization")
#
closing_lines = [growth,
               uses,
               analytics,
               summarization]
for line in closing_lines:
    line.setPartOf(standard_close)
    line.guide.priority.increment(2)
    line.guide.quality.setStandards(1,5)
#
standard_close.extend(closing_lines)
