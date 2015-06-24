#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Financials_01.Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:
0) make a bookmark
0.1) set its name
0.2) 

1) make a financials object (fin1)
1a) compare to standard
1.1) go through it, measure length, print
1.2) check partOf for every Lineitem
1.3) check bookmarks
1.4) check 3 statements
1.5) check that lineitems have guidance components

2) make another financials object (fin2)
3) make a bunch of lineitems
3.1) check that replicas work
3.2) check the summaries work
3.3) check that 3 statements work

3) make a third fin object (fin3)
4) make more lineitems
5) make a complicated hierarchy
6) check that 3 statements work


"""




#imports
import copy

from DataStructures.Modelling.BookMark import BookMark
from DataStructures.Modelling.Financials import Financials
from DataStructures.Modelling.LineItem import LineItem

from BBGlobalVariables import *




#globals
output = {}

def do():
    return output

#1: Bookmarks
bmark1 = BookMark("Classics")
bmark2 = BookMark("Novels")
bmark3 = BookMark("Poetry")
bmark2.setName("Myths")
bmark3.tag("English","old","lyric")
output["bmark1"] = bmark1
output["bmark2"] = bmark2
output["bmark3"] = bmark3

#2: Financials A
fin1 = Financials()
fin2 = Financials()

output["fin1"] = fin1
output["fin2"] = fin2
fin3 = Financials()
rev1 = LineItem(name="Revenue",value = 100)
cogs1 = LineItem(name="COGS",value = 50)
opex1 = LineItem(name="OPEX",value = 20)
sga1 = LineItem(name="SG&A",value = 10)
for L in [rev1,cogs1,opex1,sga1]:
    L.setPartOf(fin3)
mens1 = LineItem(name="Men's",value = 35)
womens1 = LineItem(name="Women's",value=42)
mens1.setPartOf(rev1)
womens1.setPartOf(rev1)
ee1 = LineItem(name="Employee Expense",value=9)
comp1 = LineItem(name="Compensation",value=6)
benefits1 = LineItem(name="Benefits",value=1)
taxes1 = LineItem(name="Payroll Taxes",value=2)
for L in [comp1,benefits1,taxes1]:
    L.setPartOf(ee1)
ee1.setPartOf(opex1)
kml1 = LineItem(name = "KML Insurance",value=5)
kml1.setPartOf(sga1)
rent1 = LineItem(name="Rent",value = 11)
rent1.setPartOf(opex1)
fin3_newContent = (fin3[:4]+
        [rev1,mens1,womens1,cogs1,
         opex1,ee1,comp1,benefits1,taxes1,rent1,sga1,kml1]+
        fin3[4:])
fin3.clear()
fin3.extend(fin3_newContent)
fin3.autoSummarize = False

sharks = LineItem(name="Sharks!!")
sharks.partOf = "Navy Seals"
fin4 = copy.deepcopy(fin3)
fin4.insert(9,sharks)
output["fin3"] = fin3
output["fin4"] = fin4
output["sharks"] = sharks

#T1.07 panel: misordered complex fins
#skip

#T1.08 panel: manage summaries
fin5 = copy.deepcopy(fin3)
fin5.autoSummarize = False
output["T1.08"]={}
output["T1.08"]["fin5"] = fin5

#T1.09: drop down replicas
fin6 = copy.deepcopy(fin3)
fin6.autoSummarize = False
output["T1.09"] = {}
output["T1.09"]["fin6"] = fin6
ddrUps = [31,32,3,3]
output["T1.09"]["ddrUps"] = ddrUps

#T1.10: panel
fin7 = copy.deepcopy(fin3)
fin7.autoSummarize = False
output["T1.10"] = {}
output["T1.10"]["fin7"] = fin7
marketing = LineItem(name="Marketing",value=7.7)
it = LineItem(name="IT",value=1.8)
rnd = LineItem(name="R&D",value = 7.3)
for L in [marketing,it,rnd]:
    L.setPartOf(sga1)
newLs = [(23,marketing),(23,it),(23,rnd)]
output["T1.10"]["newLs"] = newLs
fin8 = copy.deepcopy(fin3)

#T1.11:
freightin = LineItem(name="Freight In",value = 3.5)
freightout = LineItem(name="Freight Out",value = 4.15)
storage = LineItem(name="Storage",value = 9.2)
fin8 = copy.deepcopy(fin3)
for L in [marketing,it,rnd]:
    fin8.insert(15,L)
for L in [freightin,freightout,storage]:
    L.setPartOf(cogs1)
    fin8.insert(8,L)
output["T1.11"] = {}
output["T1.11"]["fin8"] = fin8

#T1.12:
fin9 = copy.deepcopy(fin8)
fin9.summarize()
output["T1.12"]={}
output["T1.12"]["fin9"] = fin9

#T1.13:
fin10 = copy.deepcopy(fin8)
fin10.summarize()
output["T1.13"]={}
output["T1.13"]["fin10"] = fin10





