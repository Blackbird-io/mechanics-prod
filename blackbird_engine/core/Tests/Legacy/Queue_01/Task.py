#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Queue_01.Task

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

#T4.01
testQ = MC.Queue()
output["testQ"] = testQ

#rest of code for building standard

##drF1 = MC.Driver()
##drF1.setName("drF1")
##drF2 = MC.Driver()
##drF2.setName("drF2")
##drF3 = MC.Driver()
##drF3.setName("drF3")
##bucketF = [drF1,drF2,drF3]
##for i in bucketF:
##    i.tag("bucketF")
##    i.mustBeFirst = True
##    i.canBeLast = False
##output["bucketF"]=bucketF

##drMA1 = MC.Driver()
##drMA1.setName("drMA1")
##drMA2 = MC.Driver()
##drMA2.setName("drMA2")
##drMA3 = MC.Driver()
##drMA3.setName("drMA3")
##drMA4 = MC.Driver()
##drMA4.setName("drMA4")
##drMA5 = MC.Driver()
##drMA5.setName("drMA5")
##drMA6 = MC.Driver()
##drMA6.setName("drMA6")
##bucketMA = [drMA1,drMA2,drMA3,drMA4,drMA5,drMA6]
##for i in bucketMA:
##    i.tag("bucketMA")
##output["bucketMA"]=bucketMA

##drMB1 = MC.Driver()
##drMB1.setName("drMB1")
##drMB2 = MC.Driver()
##drMB2.setName("drMB2")
##drMB3 = MC.Driver()
##drMB3.setName("drMB3")
##drMB4 = MC.Driver()
##drMB4.setName("drMB4")
##drMB5 = MC.Driver()
##drMB5.setName("drMB5")
##drMB6 = MC.Driver()
##drMB6.setName("drMB6")
##bucketMB = [drMB1,drMB2,drMB3,drMB4,drMB5,drMB6]
##for i in bucketMB:
##    i.tag("bucketMB")
##    i.canBeFirst = False
##    i.canBeLast = False
##output["bucketMB"]=bucketMB

##drL1 = MC.Driver()
##drL1.setName("drL1")
##drL2 = MC.Driver()
##drL2.setName("drL2")
##drL3 = MC.Driver()
##drL3.setName("drL3")
##bucketL= [drL1,drL2,drL3]
##for i in bucketL:
##    i.tag("bucketL")
##    i.mustBeLast = True
##    i.canBeLast = False
##    i.canBeFirst = False
##output["bucketL"]=bucketL

##slate1 = bucketF[:1]+bucketMA+bucketMB+bucketL[:1]
##slate2 = slate1 + bucketF[1:]
##slate3 = slate1 + bucketL[1:]
##slate4 = bucketMB+bucketL
##slate5 = bucketF+bucketMB
##slate6 = bucketF + bucketMA + bucketMB + bucketL
##output["slate1"] = slate1
##output["slate2"] = slate2
##output["slate3"] = slate3
##output["slate4"] = slate4
##output["slate5"] = slate5
##output["slate6"] = slate6

#slates:
  #1: F[0], bucket2, bucket3,L (good)
  #2: slate1 and insert F[1] upfront
  #3: slate2 and append L[1] at end
  #4: slate1[1:]  (no starts, nonconf)
  #5: slate1[:-1] (no ends, nonconf)
  #6: f, bucket2, bucket3, l (result should be same length as 1)



