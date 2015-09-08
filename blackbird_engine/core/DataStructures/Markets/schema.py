#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.Parameters
"""

Module that provides layout parameters for various pieces of analytics data.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
fields_CR_Details     empty list
fields_CR_Scenario    "size","price","term","structure","bb_value"
fields_CR_Reference   "bad","mid","good"
fields_CR_Landscape   "size","price"
fields_multiples      "ev"
fields_mult_ev        "x_ebitda","x_revenue"
fields_yieldCurves    "x_ebitda","x_revenue"
gl_structure_score    standard baseline structure score, set to 4

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a



#globals
fields_CR_Details = []
fields_CR_Scenario = ["size","price","term","structure","bb_value"]
fields_CR_Reference = ["bad","mid","good"]
fields_CR_Landscape = ["size","price"]
fields_multiples = ["ev"]
fields_mult_ev = ["x_ebitda","x_revenue"]
fields_yieldCurves = ["x_ebitda","x_revenue"]

gl_structure_score = 4

key_delta_ceiling = "delta_ceiling"
key_spread = "spread_per_turn"
x_axes_for_price_curves = ["x_ebitda", "x_revenue"]

#classes
#n/a
