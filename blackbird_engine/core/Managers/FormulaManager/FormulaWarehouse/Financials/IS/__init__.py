#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.FormulaManager.FormulaWarehouse.Financials.IS.__init__
"""

Package that contains content modules for Formula objects.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#packages:
from . import Cost
from . import DandA
from . import Income
from . import Interest
from . import OperatingExpense
from . import Revenue
from . import Tax
from . import Unusual

#content modules:
from . import FixedValue
from . import SourceMultiplier
from . import MonthlyExpense_FromAnnual
from . import MonthlyExpense_FromAnnual_Inflation
