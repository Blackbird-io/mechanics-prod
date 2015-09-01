#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.CreditCapacity
"""

Module defines the CreditCapacity class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class CreditCapacity  container for name-specific credit information
====================  ==========================================================

use a path to organize the order
  can have a different path: model.analytics.path
  or can attach the details to the existing path, under the analytics bookmark
    then have one path
    in one place
  problem:
    ic would then include?  

the reason why i have all this stuff in analytics is because i was trying to control order before there was a path, because i was really resistant to this idea of a path. 

but now i do have a path. so all of this pre-baked stuff is kind of non-sense. 
  the path provides ordering
  it can contain any object w a guide attribute and tags
    the object doesnt have to be a line item, though it helps if it is (for printing)
  if i need to create bundles of attributes (e.g., "ev") for standard record keeping,
    i can either create lists or classes

change "parameters" to "schema"

make the analytics path separately as default, then call always tack it on to the 
normal one; add "analytics" bookmarks

revised analytics path:
 - compute ev
 - compute abl landscape
 - compute lev landscape


"""




#imports
from .price_landscape import Landscape




#globals
#n/a

#classes
class CreditCapacity:
    """

    Class covers Blackbird estimates of credit market outcomes. Instances
    provide an interface for storing and organizing various facets of that
    information.

    The ``landscape`` attribute provides a snapshot of credit references keyed by
    price and size. Each of those keys points towards a dictionary keyed by
    their respective values (ie percent cost or size in millions). The price and
    size dictionaries then contain values for their counterpart in dictionary
    format, keyed "bad", "medium", "good". 
   
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    abl                   asset-backed loan price landscape for company
    cf                    leveraged loan price landscape for company
    bonds                 bond price landscape
    combined              combined loan price landscape for company                  
        
    FUNCTIONS:    
    combine()             pick lowest price generally? or populate a scenario w all the keys
                          #pick lowest price, can also average the prices where necessary
    ====================  ======================================================
    
    """

    def __init__(self):
        self.asset_backed = Landscape()
        self.converts = None
        self.lev_loans = Landscape()
        self.bonds = Landscape()
        self.combined = None

        self.auto_update = True
        self.landscape = CR_Landscape(standard = {})
        
    def combine(self):
        #delete current (self.combined = None)
        #combine all known landscapes
        #
        pass
    
    def build_landscape(self, yield_curve, scaling_factor,
                       standard_scenario = None, store = False):
        """


        CC.buildSizeLandscape(yCurve, scalingFactor
            [, standard_scenario = None
            [, autoPopulate = False]]) -> dict()


        Method returns a dictionary showing the reference landscape by size.
        Method computes the name-specific landscape by multiplying the generic
        leverage data in yield_curve, expressed as price per multiple, by the
        company's specific ``scaling_factor``.

        Method expects:
         -- ``yield_curve`` to be a dict-type object w a spread key
         -- ``scaling_factor`` to be a number that supports multiplication
         -- ``standard_scenario`` to be a CR_Scenario or dictionary

        If ``store`` is True, method updates instance.landscape with the
        size landscapes it generates.

        All values in the landscape are CR_Reference instances
        populated with versions of the standard scenario. The method adjusts
        the scenario for each reference point by:

         -- for size, scaling the leverage by the scaling factor (e.g., ebitda)
         -- for price, by applying the leveraged spread to the input yield
            (price goes up for bad scenarios and down for good scenarios)
         -- for structure, by manually adjusting it from loose to tight as
            leverage goes up, based on percentile rank

        """
        s_scape = {}
        p_scape = {}
        workingCurve = yield_curve.copy()
        #make a shallow copy to work on, just in case
        spread = workingCurve.pop(industry_data.key_spread)
        delta_ceiling = workingCurve.pop(industry_data.key_delta_ceiling)
        #have to pop the keys to make sure the workingCurve is all numeric; use
        #whatever key names are standard
        bad = schema.fields_CR_Reference[0]
        mid = schema.fields_CR_Reference[1]
        good = schema.fields_CR_Reference[2]
        def make_bad_price(turns):
            mid = workingCurve[turns]
            adj = spread*turns
            p = mid+adj
            p = round(p,6)
            return p
        #
        def make_mid_price(turns):
            p = workingCurve[turns]
            p = round(p,6)
            return p 
        #
        def make_good_price(turns):
            mid = workingCurve[turns]
            adj = spread*turns
            adj = min(adj,delta_ceiling)
            p = mid-adj
            p = round(p,6)
            return p
        #
        steps = sorted(workingCurve.keys())
        step_count = len(steps)
        #make the size landscape:
        for i in range(step_count):
            lev_point = steps[i]
            #
            bad_price = make_bad_price(lev_point)
            mid_price = make_mid_price(lev_point)
            good_price = make_good_price(lev_point)
            prices = [bad_price,mid_price,good_price]
            #
            scaled = lev_point * scaling_factor
            scaled = round(scaled,6)
            print("scaled: ",scaled)
            scaled = max(0,scaled)
            print("scaled = max(0,scaled)")
            print("scaled (post-adj): ",scaled)
            if not standard_scenario:
                mod_scenario = CR_Scenario()
            else:
                print("using standard_scenario")
                mod_scenario = copy.deepcopy(standard_scenario)
            print("mod_scenario['term']", mod_scenario["term"])
            mod_scenario.changeElement("size",scaled)
            print("""mod_scenario.changeElement("size",scaled)""")
            print("mod_scenario['size']", mod_scenario["size"])
            ref = CR_Reference(standard = mod_scenario)
            #now ref has the same scenario, w the ``scaled`` size, for each
            #quality key
            #adjust ref prices: 
            ref[bad].changeElement("price",bad_price)
            ref[mid].changeElement("price",mid_price)
            ref[good].changeElement("price",good_price)
            #adjust ref structure:
            rank = i/step_count
            if rank < 0.34:
                ref[bad].changeElement("structure",1)
                ref[mid].changeElement("structure",2)
                ref[good].changeElement("structure",3)
            elif rank < 0.68:
                ref[bad].changeElement("structure",4)
                ref[mid].changeElement("structure",5)
                ref[good].changeElement("structure",6)
            else:
                ref[bad].changeElement("structure",7)
                ref[mid].changeElement("structure",8)
                ref[good].changeElement("structure",9)
            s_scape[scaled] = ref
            #structure score should be btwn 0 (open)-9 (tight)
            #low leverage lending is loose, higher leverage more constrained
            #the above can be a matrix: [max_percentile: {sc_key: score}...]
##        if store:
##            self.landscape.changeElement("size",s_scape)
        return s_scape


 
