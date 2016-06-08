# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.valuation.industry_data
"""

Module defines IndustryData class, which provides a standard description of the
rate environment facing companies in a given sector at a given date. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
default_delta_ceiling max total spread btwn mid and good outcomes; 150 bps
default_spread        spread per turn btwn mid and good/bad price; 50 bps

FUNCTIONS:
n/a

CLASSES:
IndustryData          standard record for sector-specific rate environment
====================  ==========================================================
"""




#imports
from . import parameters




#globals
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
    price_curves          mid-point expected cost of debt capital as f(leverage)
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
        self.ltv_max = None
        self.price_curves = dict.fromkeys(parameters.x_axes_for_price_curves)
        self.term = None

    def set_curve(self, points, field_index = 0):
        """


        IndustryData.set_curve(points, [field_index = 0]) -> None


        Method sets the specified field in instance price_curves to a dictionary
        made from ``points``. Method supplements points with spread and delta
        ceiling data where they are missing.
        """
        curve = dict(points)
        if parameters.key_spread not in curve:
            curve[parameters.key_spread] = default_spread
        if parameters.key_delta_ceiling not in curve:
            curve[parameters.key_delta_ceiling] = default_delta_ceiling
        #
        field = parameters.x_axes_for_price_curves[field_index]
        #
        self.price_curves[field] = curve

