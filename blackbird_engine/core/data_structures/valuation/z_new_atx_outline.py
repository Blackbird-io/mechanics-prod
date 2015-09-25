"""
Revised analytics architecture


add a "comment" section to CR_Scenario

store analytics path in a financials-type object
  each attribute is a line

put "ev" and "atx" into a financials object, extend path by it

###
use a path to organize the order
  can have a different path: model.analytics.path
  or can attach the details to the existing path, under the analytics bookmark
    then have one path
    in one place
  problem:
    ic would then include all of the analytics details when forecasting int length?  

the reason why i have all this stuff in analytics is because i was trying to control order before there was a path, because i was really resistant to this idea of a path. 

but now i do have a path. so all of this pre-baked stuff is kind of non-sense. 
  the path provides ordering
  it can contain any object w a guide attribute and tags
    the object doesnt have to be a line item, though it helps if it is (for printing)
  if i need to create bundles of attributes (e.g., "ev") for standard record keeping,
    i can either create lists or classes

make the analytics path separately as default, then call always tack it on to the 
normal one; add "analytics" bookmarks

revised analytics path:
 - compute ev
 - compute abl landscape
 - compute lev landscape

    
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


    

        
        
