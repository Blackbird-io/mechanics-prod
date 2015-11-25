#PROPRIETARY AND CONFIDENTIAL
#Property of Ilya Podolyako
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Credit Market
#BBGlobalVariables
#By Ilya Podolyako

"""

This module contains settings and functions used in multiple places throughout
the Blackbird environment.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a
====================  ==========================================================
"""




# Imports
#built-in modules only
from datetime import date




# Constants
DEBUG_MODE = False
DEFAULT_MODEL_NAME = "Blank Blackbird Model"

SCREEN_WIDTH = 80
MINIMUM_PROGRESS_PER_QUESTION = 2

max_unit_count = 200
mid_unit_count = 20
high_unit_count = 50
#mid and high unit count serve as thresholds for medium and in-depth analysis.
#blackbird will analyze a model with a medium number of units reasonably well,
#and a model with a large number of units carefully. it is up to individual
#topics to support this type of depth control.
batch_count = 100
batch_count = min(batch_count, max_unit_count)
#batch count is the number of units that a company with more units than the
#max count will be split into. as batch_count goes up, models become more
#granular and more unwieldy. batch_count <= max_unit_count. the two parameters
#are distinct because Blackbird may want to capture full detail on a 200-store
#business if that means a performance hit, but when dealing with 10,000 clients
#optimize to something more compact. 

#Market
ASSUMED_ANNUAL_INFLATION = 0.03
HAIRCUT_TO_EXPECTED_VALUE = 0.20
user_correction = 0.10

#Calendar
t0 = date(2015, 6, 16)
fix_ref_date = True
#whether models always start on the same date; keep True for testing
days_in_month = 30
days_in_year = 365




