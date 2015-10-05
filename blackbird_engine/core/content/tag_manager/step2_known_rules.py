#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: alt_TagManager.step2_load_rules
"""

Module loads an instance of TagManager, registers known tags

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
loaded_tm             instance of TagManager loaded with known tags

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""




from .TagRule import TagRule
from .step1_known_tags import loaded_tM





dnt = loaded_tM.catalog["do not touch"]
spec = loaded_tM.catalog["special ex"]
hard = loaded_tM.catalog["hardcoded"]
for t in [dnt,spec,hard]:
    loaded_tM.addRule(t)

#rule 1: do not touch
dnt_rule = loaded_tM.rules[dnt]
#out (for outward facing copies): don't allow
dnt_rule["out"].place = False
#
#up (for in-period inheritance); don't alow, replace with spec
dnt_rule["up"].place = False
dnt_rule["up"].cotag = [spec]

#rule 2: special inheritance
spec_rule = loaded_tM.rules[spec]
spec_rule["out"].place = False

#rule 3: hardcoded
hard_rule = loaded_tM.rules[hard]
hard_rule["up"].place = False
hard_rule["up"].cotag = [spec]






