# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.valuation.enterprise_value
"""

Module defines the EnterpriseValue class, a standard form for storing data about
the valuation of a company as a going concern. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class CreditCapacity  container for name-specific credit information
====================  ==========================================================
"""




#imports
from ..guidance.step import Step




#globals
#n/a

#classes
class EnterpriseValue(Step):
    """

    Standard form for storing information about the enterprise value of a
    company as a going concern.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    [dcf                   line, net present value of discounted cash flows of co
    tev                   line, total enterprise value of co
    wacc                  line, weighted avg cost of capital for co used in dcf
    wacd                  line, weighted avg cost of debt for co used in dcf
    wace                  line, weighted avg cost of equity for co used in dcf
    growth                periodic growth used in dcf]
        
    FUNCTIONS:    
    n/a
    ====================  ======================================================
    
    """

    def __init__(self):
        #
        Step.__init__(self, name = "enterprise value")
                    
                
