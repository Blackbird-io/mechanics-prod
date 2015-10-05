#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: TW.Introduction.PathFinders.__init__
"""

Contains specialized packages.

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
from . import pf_generic
from . import pf_software
from . import shared_knowledge
#Warehouse packages have to import their contents. Catalog managers walk the
#directory by looking at the top-level names of the package object. Without
#imports through __init__, the walker function will not see any of the
#subfolders or their constituent modules. 

    


