#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Summarization.Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

Load script, run through interview,
output the final model
model should include interview

"""
import dill
import Shell

output = {}

def do():
    return output

#T16.01
output["T16.01"] = {}
print(output)
##use relative paths to maintain portability
p = r"scripts\retail2.pkl"
print(p)
f = open(p,"rb")
script_retail = dill.load(f)
f.close()
print("interview script: \n",script_retail)
Shell.use_script(script_retail)
msg = Shell.continuous()
M = msg[0]
output["T16.01"]["M"] = M
new_summary = M.summary
output["T16.01"]["summary"] = new_summary
print(output)
##use relative paths to maintain portability
p_s = r"tests\basic\summarization\new_summary.pkl"
f = open(p_s,"wb")
dill.dump(new_summary,f)
f.close()
print("Serialized model summary.")
##
#print 












