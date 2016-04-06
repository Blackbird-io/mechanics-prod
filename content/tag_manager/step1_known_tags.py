#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TagManager.known_tags
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





from .TagManager import TagManager





loaded_tM = TagManager()

t_bb = "|BB|"
loaded_tM.registerTag(t_bb,"bb","BLACKBIRDSTAMP","|BB|")

t_bm = "bookMark"
loaded_tM.registerTag(t_bm,"bookmark","bm","mark","bookMark")

t_built_in = "Built In"
loaded_tM.registerTag(t_built_in,"built_in")

t_cons = "consolidated"
loaded_tM.registerTag(t_cons,"consolidated")

t_dnt = "do not touch object!"
loaded_tM.registerTag(t_dnt,"do_not_touch","do not touch","dnt")

t_ddr = "dropdownreplica"
loaded_tM.registerTag(t_ddr,"ddr","dropDownReplica","dropDownReplicaTag")

t_hard = "hard coded value on object"
loaded_tM.registerTag(t_hard,"hard","hardcoded")

t_skip = "SKIP"
loaded_tM.registerTag(t_skip,"skip","SKIP","skipTag")

t_spec = "special extrapolate only!"
loaded_tM.registerTag(t_spec,"special_ex","special ex","specx")

t_sum = "summary"
loaded_tM.registerTag(t_sum,"summary","summaryTag")

t_trump = "trump!"
loaded_tM.registerTag(t_trump,"trump","trumpTag")
