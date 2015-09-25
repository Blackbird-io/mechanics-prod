#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: TopicWarehouse.__init__
"""

Module provides TopicManager with an interface to specialized packages. Module
imports all packages at __init__ so they appear as attributes that TopicManager
can walk.
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
from . import financials
from . import growth
from . import introduction
from . import management
from . import operations
from . import overview
from . import regulatory
from . import structure
from . import summary
from . import valuation


    

#globals
#this module should not contain any logic
