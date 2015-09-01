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
"""




#imports
import copy

from . import industry_data
from . import Parameters as schema


from .credit_landscape import CR_Landscape
from .CR_Reference import CR_Reference
from .Pattern import Pattern




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
    abl                   instance of ABL object
    landscape             instance of CR_Landscape (dict w Reference values)
    ll                    instance of LL object
    
    FUNCTIONS:
    buildSizeLandscape()  generates a dict of full references from a yield curve
    buildSecondaryLandscape()  organizes  existing landscape into new ref points
    trimLandscape()       cuts off ref points outside an external range
    ====================  ======================================================
    
    """

    def __init__(self):
        self.auto_update = True
        self.landscape = CR_Landscape(standard = {})
        

    def buildSizeLandscape(self, yCurve, scalingFactor,
                       standard_scenario = None,autoPopulate = False):
        """


        CC.buildSizeLandscape(yCurve, scalingFactor
            [, standard_scenario = None
            [, autoPopulate = False]]) -> dict()


        Method returns a dictionary showing the reference landscape by size.

        Method expects:
         -- yCurve to be a dict-type object w a spread key
         -- scalingFactor to be numeric & supports multiplication
         -- standard_scenario to be a CR_Scenario or dictionary

        If ``autoPopulate`` is True, method updates instance.landscape with the
        size landscapes it generates.

        #<---------------------------------------------------------------------------should call this var ``store``

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
        workingCurve = yCurve.copy()
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
        #make the size landscape:
        for i in range(len(steps)):
            lev_point = steps[i]
            #
            bad_price = make_bad_price(lev_point)
            mid_price = make_mid_price(lev_point)
            good_price = make_good_price(lev_point)
            prices = [bad_price,mid_price,good_price]
            #
            scaled = lev_point*scalingFactor
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
            rank = i/len(steps)
                #<-------------------------------------------------------------- compute length once
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
        if autoPopulate:
            self.landscape.changeElement("size",s_scape)
        return s_scape

    def buildSecondaryLandscape(self,s_scape,ref_key = "price",
                            scoring_var = "size", autoPopulate = False):
        """

        CC.buildSecondaryLandscape(s_scape,[ref_key = "price"
            [,scoring_var = "size"[,autoPopulate = False]]] -> dict

        Method builds and returns a secondary landscape using scenarios present
        in the input ``s_scape`` (usually a landscape keyed by size).

        Method goes through each reference point in s_scape. For each scenario
        within each reference point, method pulls out the value associated with
        the ``ref_key`` key (for example, ``price`` or ``structure``). bSL()
        then creates a new reference object for each unique ref_val, enters the
        reference under the ref_val in the result landscape, and enters the
        scenario that triggerred this whole operation in the reference under
        the scenario[scoring_var] key.

        The resulting dictionary contains references for each unique ref_key
        value in the input landscape, and each of those references contains
        a range of scenarios, keyed by their scoring_variable result.

        For example, this method can be used to generate a price landscape from
        a size landscape. The price landscape should be keyed by price in
        percent, so ref_key := ``price``. Each key should point towards a
        reference that contains every scenario with a given price (e.g., 8%).
        
        There may be many such scenarios, so the reference should key them by
        whatever metric describes their relative desirability (from the
        perspective of the borrower). When price is constant, size is the most
        significant variable - a company wants to borrow as much as possible at
        a given price. So in the p_scape, each reference would contain keys of
        different loan sizes, with values pointing to scenarios that describe a
        loan of that size (w/r/to structure, term, or anything else) at the
        given price (8%).
        
        NOTE: Method does **not** label scenarios as "bad","good", etc.
        The scenarios associated with any default reference keys are blank. 

        Use landscape.updateLabels() to assign specific scenarios to the keys
        after this method concludes its work.
        """
        p_scape = {}
        for ref in s_scape.values():
            for scenario in ref.values():
                pricePoint = scenario[ref_key]
                sizePoint = scenario[scoring_var]
                if pricePoint not in p_scape.keys():
                    newRef = CR_Reference()
                    newRef.setAll(ref_key,pricePoint)
                    p_scape[pricePoint] = newRef
                p_scape[pricePoint][sizePoint] = scenario
        if autoPopulate:
            self.landscape.changeElement(ref_key,p_scape)
        return p_scape

        #<--------------------------------------------------call this flip_landscape or invert_landscape
        #main parameter should be called ref_scape

    def trimLandscape(self,field,lo_bound=None,hi_bound=None):
        """


        CreditCapacity.trimLandscape(field,lo_bound=None,hi_bound=None) -> None


        Method for specified field in landscape, delete items w keys smaller
        than the lo_bound or larger than the hi_bound. 
        """
        old = self.landscape.keepForecasts
        self.landscape.keepForecasts = True
        if lo_bound:
            ref_lo = self.landscape.forecast(ask=lo_bound, field=field)
        if hi_bound:
            ref_hi = self.landscape.forecast(ask=hi_bound, field=field)
        F = self.landscape[field]
        points = sorted(F.keys())
        for p in points:
            if lo_bound and (p < lo_bound):
                F.pop(p)
            elif hi_bound and (p > hi_bound):
                F.pop(p)
        self.landscape.keepForecasts = old
        #<------------------------------------------------------------this should be landscape.trim()

