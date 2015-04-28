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




#imports
import dill
import os
import Shell




#globals
output = {}

#functions
def do():
    return output

#T11.01
output["T11.01"] = {}
print(output)
p = r"scripts\retail2.pkl"
p = os.path.normpath(p)
#make path portable
#
print(p)
f = open(p,"rb")
print(f)
script_retail = dill.load(f)
f.close()
del p
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
p_s = r"tests\basic\Model_01_Retail\new_model.pkl"
p_s = os.path.normpath(p_s)
#make path portable
#
f = open(p_s,"wb")
dill.dump(M,f)
f.close()
print("Model created and serialized.")













