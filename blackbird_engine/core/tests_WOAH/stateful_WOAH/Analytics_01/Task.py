#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Analytics_01.Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

Load sample model (filled out and all)
Run analytics
get summary
get price forecast
get size forecast
save all to output

Grader compares result
"""
import dill
import Shell

output = {}

def do():
    return output
#
c = """

Running Analytics_01

Task loads a simple standard model and puts it through session controller's
analytics routine (SessionController.getAnalytics). Task then runs four simple
forecasts on the Model and saves the result. 

"""
print(c)
#
#T12.01: get analytics
output["T12.01"] = {}
output["T12.02"] = {}
output["T12.03"] = {}
print(output)
p = r"Tests\Basic\Analytics_01\source_model.pkl"
print(p)
f = open(p,"rb")
print(f)
sM = dill.load(f)
f.close()
print("starting model: \n",sM)
uM = Shell.SessionController.process_analytics(sM)
print ("uM = Shell.SessionController.process_analytics(sM)")
print("updated model:  \n", uM)
print("starting model: \n", sM)
print("uM is sM:       \n", uM == sM)
output["T12.01"]["uM"] = uM
output["T12.01"]["atx"] = uM.analytics
#T12.02: get summary
l_sum = uM.analytics.cc.landscape.getSummary()
output["T12.02"]["l_sum"] = l_sum
#T12.03: get a couple forecasts
ref5mm = uM.analytics.cc.landscape.forecast(ask = 5000000)
ref10mm = uM.analytics.cc.landscape.forecast(ask = 10000000)
ref5pct = uM.analytics.cc.landscape.forecast(field = "price", ask = 0.05)
ref10pct = uM.analytics.cc.landscape.forecast(field = "price", ask = 0.10)
output["T12.03"]["ref5mm"] = ref5mm
output["T12.03"]["ref10mm"] = ref10mm
output["T12.03"]["ref5pct"] = ref5pct
output["T12.03"]["ref10pct"] = ref10pct
print(output["T12.03"].keys())
p_u = r"tests\basic\Analytics_01\updated_model.pkl"
f = open(p_u,"wb")
dill.dump(uM,f)
f.close()
print("Performed analytics and saved updated model.")













