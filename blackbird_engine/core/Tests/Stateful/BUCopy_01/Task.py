#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\BUCopy_01\Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

Load sample model (filled out and all)
Make a copy of the top period
save all to output.

Grader compares the original and the copy

"""
import dill

output = {}

def do():
    return output
#
c = """

Running Copy_01

Task loads a simple standard model and makes a class-specific copy of the top
business unit in the Model's current period.

Grader checks that the copy compares equal to the original, is deep in the right
places (points towards independent components, drivers, etcetera), and shallow
in others (points towards the same Model and the same period).
"""

print(c)
#
#T13.01: get analytics
output["T13.01"] = {}
print(output)
p = r"Tests\Basic\BUCopy_01\source_model.pkl"
print(p)
f = open(p,"rb")
print(f)
sM = dill.load(f)
f.close()
print("starting model: \n",sM)
s_topBU = sM.currentPeriod.content
s_topBU.fillOut()
print("s_topBU.fillOut() \n")
print("top business uint: \n", s_topBU)
#
#T13.01: make a copy of the top business unit
print("T13.01: make a class-specific copy of topBU. enforce rules.")
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
output["T13.01"]["topBU"] = s_topBU
output["T13.01"]["c1"] = c1
output["T13.01"]["c2"] = c2
output["T13.01"]["cc3"] = cc3
print("Successfully loaded model and copied its top business unit.")













