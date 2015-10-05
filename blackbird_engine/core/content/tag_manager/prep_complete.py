#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: alt_TagManager.prep_complete
"""

Module provides persistent interface to an instance of tag manager ready for
external use. The module tracks the last step in preparation and points to
the completed output there.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
TM                    TagManager instance that has gone through all prep steps

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""

from .step2_known_rules import loaded_tM

loaded_tagManager = loaded_tM
