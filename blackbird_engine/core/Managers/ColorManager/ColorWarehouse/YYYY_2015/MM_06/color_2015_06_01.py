#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: CW.y_2015.m_08.color_082415
"""

Market color as of Aug. 24, 2015
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""




#imports
from DataStructures.Valuation import industry_data
from DataStructures.Valuation.market_color import MarketColor




#globals
color_content = True
color = MarketColor(author = "IOP", ref_date_iso = "2015-06-01")
key_delta_ceiling = industry_data.key_delta_ceiling
key_spread = industry_data.key_spread


#configure
#industry 0: generic
k = None
#
color.add_industry(k)
industry = color[k]
#
industry.ev_x_ebitda = 8
industry.debt_x_ebitda = 5
industry.ltv_max = 0.80
industry.term = 3
generic_x_ebitda = [(0.5,0.03),
                    (1.0,0.04),
                    (1.5,0.04),
                    (2.0,0.05),
                    (2.5,0.07),
                    (3.0,0.07),
                    (3.5,0.10),
                    (4.0,0.10),
                    (4.5,0.14),
                    (5.0,0.14),
                    (key_spread,0.0050),
                    (key_delta_ceiling,0.0150)]
#spread is in bps
industry.set_curve(generic_x_ebitda)
del generic_x_ebitda
#delete to avoid accidental cross-references

#industry 1: retail
k = "retail"
#
color.add_industry(k)
industry = color[k]
#
industry.ev_x_ebitda = 6
industry.debt_x_ebitda = 5
industry.ltv_max = 0.80
industry.term = 3
k_x_ebitda = [(0.5,0.05),
              (1.0,0.05),
              (1.5,0.06),
              (2.0,0.06),
              (2.5,0.08),
              (3.0,0.08),
              (3.5,0.12),
              (4.0,0.12),
              (4.5,0.16),
              (5.0,0.16),
              (key_spread,0.0100),
              (key_delta_ceiling,0.0200)]
#spread is in bps
industry.set_curve(k_x_ebitda)

#industry 2: software
k = "software"
#
color.add_industry(k)
industry = color[k]
#
industry.ev_x_ebitda = 10
industry.debt_x_ebitda = 5
industry.ltv_max = 0.70
industry.term = 5
k_x_ebitda = [(0.5,0.03),
              (1.0,0.03),
              (1.5,0.03),
              (2.0,0.04),
              (2.5,0.04),
              (3.0,0.04),
              (3.5,0.08),
              (4.0,0.08),
              (key_spread,0.0075),
              (key_delta_ceiling,.0100)]
#spread is in bps
#NOTE: shorter yield curve
industry.set_curve(k_x_ebitda)

