#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\BusinessUnit_03.Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

"""
import copy
import time
import random
from BBGlobalVariables import *
from LTDEX_0_ObjectLibraries import ModelComponents as MC

output = {}

def do():
    return output

refTime6 = 1416340463.27548
lifeSpan6 = 60*60*24*30*12*20
baseAge = 60*60*24*30*12*5
#T6.01:
A1 = MC.BusinessUnit()
A1.setName("WalMart")
output["T6.01"] = {}
output["T6.01"]["A1"] = A1
#
#
#T6.02:
A2 = copy.deepcopy(A1)
#deep copy to not modify prior units in place
#need clean versions for each stage
Aa1 = MC.BusinessUnit()
Aa1.setName("Atlanta")
Aa2 = MC.BusinessUnit("Baltimore")
Aa3 = MC.BusinessUnit("Chicago")
Aa4 = MC.BusinessUnit("Denver")
Aa5 = MC.BusinessUnit("El Paso")
batch02 = [Aa1,Aa2,Aa3,Aa4,Aa5]
for bu in batch02:
    bu.lifeCycle.setInitialAge(baseAge,refTime6)
    bu.lifeCycle.setLifeSpan(lifeSpan6)
    A2.addComponent(bu)
A2.fillOut()
output["T6.02"] = {}
output["T6.02"]["A2"] = A2
output["T6.02"]["batch02"] = batch02
#
#
#T6.03:
A3 = copy.deepcopy(A2)
output["T6.03"] = {}
output["T6.03"]["A3"] = A3
#make component units
Ab1 = MC.BusinessUnit("Albany, GA")
Ab2 = MC.BusinessUnit("Birmingham, AL")
Ab3 = MC.BusinessUnit("Charlotte, NC")
Ab4 = MC.BusinessUnit("Detroit")
Ab5 = MC.BusinessUnit("Erie")
batch03 = [Ab1,Ab2,Ab3,Ab4,Ab5]
for bu in batch03:
    bu.lifeCycle.setInitialAge(baseAge,refTime6)
    bu.lifeCycle.setLifeSpan(lifeSpan6)
output["T6.03"]["batch03"] = batch03
#make financials
fin03 = MC.Financials()
rev1 = MC.LineItem(name="Revenue",value = 100)
cogs1 = MC.LineItem(name="COGS",value = 50)
opex1 = MC.LineItem(name="OPEX",value = 20)
sga1 = MC.LineItem(name="SG&A",value = 10)
for L in [rev1,cogs1,opex1,sga1]:
    L.setPartOf(fin03)
mens1 = MC.LineItem(name="Men's",value = 35)
womens1 = MC.LineItem(name="Women's",value=42)
mens1.setPartOf(rev1)
womens1.setPartOf(rev1)
ee1 = MC.LineItem(name="Employee Expense",value=9)
comp1 = MC.LineItem(name="Compensation",value=6)
benefits1 = MC.LineItem(name="Benefits",value=1)
taxes1 = MC.LineItem(name="Payroll Taxes",value=2)
for L in [comp1,benefits1,taxes1]:
    L.setPartOf(ee1)
ee1.setPartOf(opex1)
kml1 = MC.LineItem(name = "KML Insurance",value=5)
kml1.setPartOf(sga1)
rent1 = MC.LineItem(name="Rent",value = 11)
rent1.setPartOf(opex1)
newFinContent = (fin03[:4]+
        [rev1,mens1,womens1,cogs1,
         opex1,ee1,comp1,benefits1,taxes1,rent1,sga1,kml1]+
        fin03[4:])
fin03.clear()
fin03.extend(newFinContent)
output["T6.03"]["fin03"] = fin03
for bu in [Ab1,Ab2,Ab3]:
    AbFins = copy.deepcopy(fin03)
    AbFins.setPartOf(bu)
    bu.financials.replaceWithTemplate(AbFins)
    #should fins get set to partOf?
    A3.addComponent(bu)
#
fin04 = copy.deepcopy(fin03)
marketing = MC.LineItem(name="Marketing",value=7.7)
it = MC.LineItem(name="IT",value=1.8)
rnd = MC.LineItem(name="R&D",value = 7.3)
for L in [marketing,it,rnd]:
    L.setPartOf(sga1)
    fin04.insert(15,L)
fin04.setPartOf(Ab4)
output["T6.03"]["fin04"] = fin04
Ab4.financials.replaceWithTemplate(fin04)
A3.addComponent(Ab4)
#
fin05 = copy.deepcopy(fin03)
freightin = MC.LineItem(name="Freight In",value = 3.5)
freightout = MC.LineItem(name="Freight Out",value = 4.15)
storage = MC.LineItem(name="Storage",value = 9.2)
for L in [marketing,it,rnd]:
    fin05.insert(15,L)
for L in [freightin,freightout,storage]:
    L.setPartOf(cogs1)
    fin05.insert(8,L)
fin05.setPartOf(Ab5)
output["T6.03"]["fin05"] = fin05
Ab5.financials.replaceWithTemplate(fin05)
A3.addComponent(Ab5)
#A3, Ab4, and Ab5 already in output[T6.03]; objects modified in place
A3_2 = copy.deepcopy(A3)
A3_3 = copy.deepcopy(A3)
A3_2.consolidate()
A3_3.filled = False
A3_3.fillOut()
output["T6.03"]["A3_2"] = A3_2
output["T6.03"]["A3_3"] = A3_3
#
#


#other functionality:
        #clear financials
        #add some components
        #print
        
## new test (w drivers in the mix):
#add drivers to units w default financials
#rev
#cogs
#fillOut
#compare A to B
#fillOut again
#compare A to B

##add a bunch of other bunits w drivers to
#second item
#

## check if derive trumps correctly (fixed>derive>consolidate)
#
#












