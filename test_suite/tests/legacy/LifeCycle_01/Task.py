#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\LifeCycle_01.Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

"""
import copy
import time
from BBGlobalVariables import *
from LTDEX_0_ObjectLibraries import ModelComponents as MC

output = {}

def do():
    return output

#T3.01: LifeStages
output["T3.01"] = {}
youth = MC.LifeStage("youth",0,24)
youth.makeFirst()
maturity = MC.LifeStage("maturity",25,65)
decline = MC.LifeStage("decline",66,78)
decline.makeLast()
stages_1 = [youth,maturity,decline]
old = MC.LifeStage("old",79,90)
stages_2 = copy.deepcopy(stages_1)
stages_2[2].ends = old.starts-1
stages_2.append(old)
output["T3.01"]["old"] = old
output["T3.01"]["stages_1"] = stages_1
output["T3.01"]["stages_2"] = stages_2

#T3.02:
output["T3.02"] = {}
lc1 = MC.LifeCycle()
lc2 = MC.LifeCycle()
lc3 = MC.LifeCycle()
output["T3.02"]["lc1"] = lc1
output["T3.02"]["lc2"] = lc2
output["T3.02"]["lc3"] = lc3

#T3.03:
output["T3.03"] = {}
refTime3 = 1416340463.27548
lifeSpan3 = 60*60*24*30*12*20
#20yr life span in seconds
age3_1 = 60*60*24*30*48
#48mo age in seconds
lc4 = copy.deepcopy(lc1)
lc5 = copy.deepcopy(lc2)
lc6 = copy.deepcopy(lc3)
lc7 = copy.deepcopy(lc3)
lc8 = copy.deepcopy(lc3)
for lc in [lc4,lc5,lc6,lc7,lc8]:
    lc.setLifeSpan(lifeSpan3)
lc4.setInitialAge(refDate=refTime3)
lc5.setInitialAge(age3_1,refTime3)
lc6.setInitialAge(age3_1,refDate=lc5.dateBorn)
lc7.setInitialAge(age3_1*2,refTime3)
#lc7 is the same age as lc6
lc8.setInitialAge(stages_2[-1].starts*0.95,refTime3)
lc8_4 = copy.deepcopy(lc8)
lc8_5 = copy.deepcopy(lc8)
output["T3.03"]["lc4"] = lc4
output["T3.03"]["lc5"] = lc5
output["T3.03"]["lc6"] = lc6
output["T3.03"]["lc7"] = lc7
output["T3.03"]["lc8"] = lc8
lc8_4 = copy.deepcopy(lc8)
lc8_5 = copy.deepcopy(lc8)
incrementA = 60*60*24*30*12*2
lc8_4.makeOlder(incrementA)
lc8_5.moveForwardInTime(incrementA)
output["T3.03"]["lc8_4"] = lc8_4
output["T3.03"]["lc8_5"] = lc8_5

#T3.04:
output["T3.04"] = {}
output["T3.04"]["stages_2"] = copy.deepcopy(stages_2)
stages_3 = copy.deepcopy(stages_2)
stages_3[0].ends = 10
stages_3[1].starts = 11
#set all to new lifestages
output["T3.04"]["stages_3"] = stages_3
lc9 = copy.deepcopy(lc4)
lc10 = copy.deepcopy(lc5)
lc11 = copy.deepcopy(lc6)
lc12 = copy.deepcopy(lc7)
lc13 = copy.deepcopy(lc8)
lifeSpan4 = lifeSpan3/2
lc11.setLifeSpan(lifeSpan4)
lc12.setLifeSpan(lifeSpan4)
lc12.kill()
slate = [lc9,lc10,lc11,lc12,lc13]
output["T3.04"]["slate"] = slate



