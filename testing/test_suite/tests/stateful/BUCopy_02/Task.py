#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\BUCopy_02\Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

Load sample model (filled out and all)
Tag a line item as "hard coded"
Tag a driver as "do not touch"
Save all to output.

Grader compares the original and the copy
"""
import dill

output = {}

def do():
    return output
#
c = """

Running BUCopy_02

Test evaluates whether copy methods properly follow tag rules.

Task loads a simple standard model with a developed top business unit. Task
then tags one of the line items in a ground-level component as hard-coded.
Task also tags a driver in the same component as "do not touch".

Task then proceeds to make several copies of the top business unit.

Grader checks that hard-coded tag travelled out but the dnt tag did not. 
"""
print(c)
#
#T14.01: Load model and tag catalog
print("#T14.01: Load model and tag catalog, get necessary tag objects.")
output["T14.01"] = {}
print(output)
p = r"Tests\Basic\BUCopy_02\source_model.pkl"
print(p)
f = open(p,"rb")
print(f)
sM = dill.load(f)
f.close()
print("starting model: \n",sM)
s_topBU = sM.currentPeriod.content
s_topBU.fillOut()
print("s_topBU.fillOut() \n")
print("top business unit: \n", s_topBU)
#
from Managers.tag_manager import loaded_tagManager as tag_manager
t_dnt = tag_manager.catalog["dnt"]
t_hard = tag_manager.catalog["hard"]
print("""
from Managers.tag_manager import loaded_tagManager as tag_manager
t_dnt = tag_manager.catalog["dnt"]
t_hard = tag_manager.catalog["hard"]
""")
print("t_dnt:  %s" % t_dnt)
print("t_hard: %s\n" % t_hard)
#
#T14.02: locate and modify component
c = ""
c += "T14.02: locate component no. 4, tag a line as hard-coded and a driver"
c += "as dnt.\n"
print(c)
output["T14.02"] = {}
ordered_bbids = sorted(s_topBU.components.keys())
lab_bbid = ordered_bbids[3]
lab_comp = s_topBU.components[lab_bbid]
print("""
ordered_bbids = sorted(s_topBU.components.keys())
lab_bbid = ordered_bbids[3]
lab_comp = s_topBU.components[lab_bbid]
""")
print("lab comp bbid: \n%s\n" % lab_comp.id.bbid)
#
l_rent = lab_comp.financials[9]
l_util = lab_comp.financials[10]
l_rent.tag(t_hard)
dr_util = lab_comp.drivers.getDrivers(l_util.name)[0]
dr_util.tag(t_dnt)
print("""
l_rent = lab_comp.financials[9]
l_util = lab_comp.financials[10]
l_rent.tag(t_hard)
dr_util = lab_comp.drivers.getDrivers(l_util.name)[0]
dr_util.tag(t_dnt)
""")
print("lab line: \n%s\n" % l_rent)
print("lab line tags: \n%s\n" % l_rent.allTags)
print("lab driver bbid: \n%s\n" % dr_util.id.bbid)
output["T14.02"]["lab_comp_bbid"] = lab_comp.id.bbid
output["T14.02"]["lab_comp"] = lab_comp
output["T14.02"]["lab_dr_bbid"] = dr_util.id.bbid
output["T14.02"]["lab_dr"] = dr_util
output["T14.02"]["lab_line"] = l_rent
output["T14.02"]["t_dnt"] = t_dnt
print("""
output["T14.02"]["lab_comp_bbid"] = lab_comp.id.bbid
output["T14.02"]["lab_comp"] = lab_comp
output["T14.02"]["lab_dr_bbid"] = dr_util.id.bbid
output["T14.02"]["lab_dr"] = dr_util
output["T14.02"]["lab_line"] = l_rent
output["T14.02"]["t_dnt"] = t_dnt
""")
#
print("T14.03: make copies, enforce rules.")
output["T14.03"] = {}
c1 = s_topBU.copy(enforce_rules = True)
print("c1 = s_topBU.copy(enforce_rules = True)")
print("\n")
#
#make a second copy of the topBU, turn off period, and copy the copy.
print("make a second copy of topBU, set its period to None, copy it again.")
c2 = s_topBU.copy(enforce_rules = True)
c2.period = None
cc3 = c2.copy()
print("""
c2 = s_topBU.copy(enforce_rules = True)
c2.period = None
cc3 = c2.copy()
""")
output["T14.01"]["topBU"] = s_topBU
output["T14.03"]["c1"] = c1
output["T14.03"]["c2"] = c2
output["T14.03"]["cc3"] = cc3
print("""
output["T14.01"]["topBU"] = s_topBU
output["T14.03"]["c1"] = c1
output["T14.03"]["c2"] = c2
output["T14.03"]["cc3"] = cc3
""")
print("Successfully completed test.")













