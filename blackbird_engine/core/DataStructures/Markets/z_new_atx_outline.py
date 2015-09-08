"""
Revised analytics architecture

analytics is a container object
has the following attrs:
  - ev
  - credit

can also be flat
can call it all "value" or "valuation"

valuation would be an expanded version of the credit capacity object we have today
- abl
- lev
- bonds
- combined

landscape would handle the "build" and "flip" methods
    #should also have a pretty-print
    #sort and print all keys in order, w values

all objs should have guide attrs

add a "comment" section to CR_Scenario

store analytics path in a financials-type object
  each attribute is a line

put "ev" and "atx" into a financials object, extend path by it

    
"""

class Valuation:
    """
    ev
    credit
    """
    def __init__(self):
        self.ev = EnterpriseValue()
        self.credit = CreditCapacity()

class EnterpriseValue:
    def __init__(self):
        self.dcf = None
        self.blah = None
    #purely storage and guidance
    #

#
#also make a special path add-on for valuation


    

        
        
