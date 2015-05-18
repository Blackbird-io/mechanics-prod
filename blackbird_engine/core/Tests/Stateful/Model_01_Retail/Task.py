#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Model_01_Retail.Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

Load script, run through interview,
output the final model

"""
import dill
import Shell

from Scripts import Retail2_Raw

output = {}

def do():
    return output

#T11.01
output["T11.01"] = {}
print(output)
##use relative paths to maintain portability
c = """
Already imported Retail2_Raw module from scripts:

Module: %s\n
"""
c = c % Retail2_Raw
print(c)
#
script_retail = Retail2_Raw.answers
c = """script_retail = Retail2_Raw.answers"""
print(c)
#
print("interview script: \n",script_retail)
Shell.use_script(script_retail)
msg = Shell.continuous()
M = msg[0]
print(M)
topBU = M.currentPeriod.content
topBU.fillOut()
output["T11.01"]["M"] = M
print(output)
##use relative paths to maintain portability
p_s = r"tests\stateful\Model_01_Retail\new_model.pkl"
f = open(p_s,"wb")
dill.dump(M,f)
f.close()
print("Model created and serialized.")













