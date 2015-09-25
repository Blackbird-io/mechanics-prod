#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.EnterpriseValue
"""

Module defines the EnterpriseValue class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class EnterpriseValue container for name-specific valuation
====================  ==========================================================
"""




#imports
from DataStructures.Modelling.LineItem import LineItem

from .Pattern import Pattern




#globals
#n/a

#classes
class EnterpriseValue(Pattern):
    """

    Class covers Blackbird estimates of business value as a going concern for
    both the active model and comparable companies.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    observedMultiples     dict of ev_x multiples actually stipulated for co
    dcf                   line,net present value of discounted cash flows of co
    tev                   line, total enterprise value of co
    wacc                  line, weighted avg cost of capital for co used in dcf
    wacd                  line, weighted avg cost of debt for co used in dcf
    wace                  line, weighted avg cost of equity for co used in dcf
    growth                periodic growth used in dcf
      
    FUNCTIONS:
    #updateDCF
    ====================  ======================================================
    """

    def __init__(self,name = "EnterpriseValue"):
        Pattern.__init__(self, name)
        comps = {}
        #comps can later split into public and private and turn into a Pattern
        #as well
        dcf = LineItem(name="dcf")
        multiples = Pattern(name="Observed Multiples")
        tev = LineItem(name = "tev")
        wacc = LineItem(name = "wacc")
        wacd = LineItem(name = "wacd")
        wace = LineItem(name = "wace")
        growth = LineItem(name = "growth")
        #here, growth can just be a line w a single value and no other items
        #but the value can be a dictionary of references, including one called
        #active
        self.addElement("comps",comps)
        self.addElement("dcf",dcf)
        self.addElement("observedMultiples",multiples)
        self.addElement("tev",tev)
        self.addElement("wacc",wacc)
        self.addElement("wacd",wacd)
        self.addElement("wace",wace)   
