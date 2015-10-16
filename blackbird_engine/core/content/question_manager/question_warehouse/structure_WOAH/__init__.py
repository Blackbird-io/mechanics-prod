#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: QuestionWarehouse.Structure.__init__
"""

Package contains content modules for questions about business structure.  

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
n/a

MODULES:
n/a
====================  ==========================================================
"""




#imports
#
#must import any modules contained here at init for manager to see and add to
#catalog
#
from . import first_store_open
from . import latest_store_open
from . import months_to_unit_maturity
from . import number_of_units
from . import unit_life_span
from . import months_to_lease_store
from . import months_to_open_store
##from . import Any_or_Number_SignedStoreLeases
from . import number_signed_store_leases

#
from . import subscriber_life_range
from . import subscriber_count
from . import subscription_term_months
from . import subscriber_seats_average
from . import subscriber_seats_total_paying
##from . import goods_or_services
