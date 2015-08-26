#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.industry_data
"""

Module defines IndustryData class, which provides a standard description of the
rate environment facing companies in a given sector at a given date. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
key_delta_ceiling
key_spread
keys_landscape

FUNCTIONS:
n/a

CLASSES:
IndustryData          standard record for sector-specific rate environment
====================  ==========================================================
"""




#imports
#n/a





#globals
#formatting parameters
key_delta_ceiling = "delta_ceiling"
key_spread = "spread_per_turn"
keys_landscape = ["x_ebitda", "x_revenue"]
#
#leverage function parameters
default_delta_ceiling = 0.0150
default_spread = 0.0050

#classes
class IndustryData:
    """

    IndustryData objects provide a standard format for describing how the value
    investment universe views companies in a given sector at a point in time.

    #<------------------------------------------------------------------------------------ should store multiples as size_charts    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    [debt_x_ebitda         leverage multiple(s) on ebitda
    debt_x_revenue        leverage multiple(s) on revenue
    ev_x_ebitda           enterprise value multiple(s) on ebitda
    ev_x_revenue          enterprise value multiple(s) on revenue] #<------------------- values should be size charts
    industry_name         
    landscape             mid-point expected cost of debt capital as f(leverage)
    ltv_max               maximum loan to enterprise value (leverage) ratio
    term                  industry 
    
    FUNCTIONS:
    set_curve()           populates landscape field with datapoints
    ====================  ======================================================
    """
    def __init__(self, industry_name):
        self.ev_x_ebitda = None
        self.debt_x_ebitda = None
        self.industry = industry_name
        self.landscape = dict.fromkeys(keys_landscape)
        self.ltv_max = None
        self.term = None

    def set_curve(self, points, field_index = 0):
        """


        IndustryData.set_curve(points, [field_index = 0]) -> None


        Method sets the specified field in instance landscape to a dictionary
        made from ``points``. Method supplements points with spread and delta
        ceiling data where they are missing.
        """
        curve = dict(points)
        if key_spread not in curve:
            curve[key_spread] = default_spread
        if key_delta_ceiling not in curve:
            curve[key_delta_ceiling] = default_delta_ceiling
        #
        field = keys_landscape[field_index]
        #
        self.landscape[field] = curve

