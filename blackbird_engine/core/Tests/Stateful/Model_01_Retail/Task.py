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

output = {}

def do():
    return output

#T11.01
output["T11.01"] = {}
print(output)
##full_p = r"c:\blackbird\engine\diagnostics\scripts\retail2.pkl"
##use relative paths to maintain portability
p = r"scripts\retail2.pkl"
print(p)
f = open(p,"rb")
print(f)
script_retail = dill.load(f)
f.close()
print("interview script: \n",script_retail)
Shell.use_script(script_retail)
msg = Shell.continuous()
M = msg[0]
print(M)
topBU = M.currentPeriod.content
topBU.fillOut()
output["T11.01"]["M"] = M
print(output)
##full_p_s = r"c:\blackbird\engine\diagnostics\tests\basic\Model_01_Retail\new_model.pkl"
##use relative paths to maintain portability
p_s = r"tests\basic\Model_01_Retail\new_model.pkl"
f = open(p_s,"wb")
dill.dump(M,f)
f.close()
print("Model created and serialized.")













