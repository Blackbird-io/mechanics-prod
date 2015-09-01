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

question:
  to what extent should i integrate LineItem into the mix
  desirable lineitem features:
    - printing
    - combination of other attrs used for guidance and matching
  can make all of these things lineItems I guess

pull LineItem formatting method into a new module called printing tools

store analytics path in a financials-type object
  each attribute is an object

class LineBase:
    guide
    tags
    __str__

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


class CreditCapacity:
    def __init__(self):
        self.abl = Landscape()
        self.lev = Landscape()
        self.bonds = Landscape()
        self.combined = None

    def combine(self):
        #combine all known landscapes into combo
        #always start from scratch
            #create new landscape instance
            #build landscape by size, manually
            #invert landscape into price through method
            #
        #two options:
            #1) for every size, take only if no other curve has same or larger size at a lower price
            #(always take the lowest price); discards known datapoints
            #2) for every size, take all datapoints, keyed by price
            #then have to label them
            #and can have very wide dispersion
            #
        #can also have a smoothing feature:
            #w/in [10]% of the end of a curve, take average, not lowest
        pass

#

    

        
        
