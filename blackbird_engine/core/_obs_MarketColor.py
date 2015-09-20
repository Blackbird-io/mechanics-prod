#Blackbird Environment
#Market Color Module

#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#1. General indicators
annualInflation = 0.03
standardUnderstatement = 0.10

#2. Industry multiples

keys_industry = ["ev_x_ebitda","debt_x_ebitda","ltv_max","term","landscape"]
keys_landscape = ["x_ebitda","x_revenue"]
keys_x_ebitda = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
key_spread = "spread_per_turn"
key_delta_ceiling = "delta_ceiling"

industryColor = {}
#market color should always have the same interface
#can have size adjustments, for example


#2.1. default
k = None
industryColor[k] = {}
industryColor[k]["ev_x_ebitda"] = 8
industryColor[k]["debt_x_ebitda"] = 5
industryColor[k]["ltv_max"] = 0.80
industryColor[k]["term"] = 3
industryColor[k]["landscape"] = dict.fromkeys(keys_landscape)
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
industryColor[k]["landscape"]["x_ebitda"] = dict(generic_x_ebitda)

#2.2. retail
k = "retail"
industryColor[k] = {}
industryColor[k]["ev_x_ebitda"] = 6
industryColor[k]["debt_x_ebitda"] = 5
industryColor[k]["ltv_max"] = 0.80
industryColor[k]["term"] = 3
industryColor[k]["landscape"] = dict.fromkeys(keys_landscape)
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
industryColor[k]["landscape"]["x_ebitda"] = dict(k_x_ebitda)

#2.3. tech
k = "tech"
industryColor[k] = {}
industryColor[k]["ev_x_ebitda"] = 10
industryColor[k]["debt_x_ebitda"] = 5
industryColor[k]["ltv_max"] = 0.70
industryColor[k]["term"] = 5
industryColor[k]["landscape"] = dict.fromkeys(keys_landscape)
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
industryColor[k]["landscape"]["x_ebitda"] = dict(k_x_ebitda)







