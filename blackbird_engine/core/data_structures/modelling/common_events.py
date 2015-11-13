#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.common_events
"""

Flat module, contains strings that name common business events. By using these
keys, you maximize the probability that the engine recognizes your event and
acts appropriately.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:

#basic events
KEY_CONCEPTION        str; recommended key for conception event
KEY_BIRTH             str; recommended key for birth event
KEY_DEATH             str; recommended key for death event
KEY_MATURITY          str; recommended key for onset of maturity
KEY_OLD_AGE           str; recommended key for onset of old age

#advanced events    
KEY_KILLED            shutting a unit down ahead of schedule
KEY_RENOVATION        investing in a unit to extend its life
KEY_TERM_RENEWAL      a relationship begins another term

FUNCTIONS:
n/a

CLASSES:
n/a
====================  ==========================================================
"""



# Imports
# n/a




# Constants
KEY_CONCEPTION = "conception"
KEY_BIRTH = "birth"
KEY_DEATH = "death"

KEY_MATURITY = "maturity"
KEY_OLD_AGE = "old age"

KEY_KILLED = "killed"
KEY_RENOVATION = "renovation"
KEY_TERM_RENEWAL = "term renewal"

# Classes
# n/a

# Should not have any logic here. 
