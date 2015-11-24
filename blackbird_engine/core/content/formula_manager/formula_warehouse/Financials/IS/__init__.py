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
from . import annual_value_with_inflation
from . import annual_sized_value_with_inflation
from . import component_line_multiplier
from . import fixed_value
from . import monthly_sized_value_fixed
from . import monthly_sized_value_with_inflation
from . import monthly_value_with_inflation

from . import monthly_from_annual
from . import monthly_from_annual_inflation
from . import source_multiplier

from . import perpetual_monthly_from_annual
from . import perpetual_monthly_from_annual_inflation

