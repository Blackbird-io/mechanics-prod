#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.price_landscape
"""

Module defines container that computes and stores price data surfaces.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
bad_label             from schema for reference fields
mid_label             from schema for reference fields
good_label            from schema for reference fields

FUNCTIONS:
n/a

CLASSES:
CR_Landscape          template for credit landscape objects (reference values)
====================  ==========================================================
"""




#imports
from Tools import for_pricing_credit as pricing_tools

from . import schema

from .CR_Reference import CR_Reference
from .CR_Scenario import CR_Scenario




#globals
bad_label = schema.fields_CR_Reference[0]
mid_label = schema.fields_CR_Reference[1]
good_label = schema.fields_CR_Reference[2]

#classes
class Landscape(dict):
    """

    Class provides a dict-like container for tracking credit landscapes. Each
    key should point to a dictionary where values are CR_References.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    keep_forecasts        bool, if True, keep forecasts.
    
    FUNCTIONS:
    build_size()          construct size-based surface from price curve
    forecast()            returns a reference for a price or size ask
    get_summary()         returns dict w min & max values for each field
    label()               select scenarios in surface that are bad/mid/good
    pivot()               organize existing data into a surface along new axes
    trim()                cuts off ref points outside an external range
    ====================  ======================================================
    """
    def __init__(self):
        dict.__init__(self)
        self.keep_forecasts = True

    def build_main(self, price_curve, multiplier,
                   standard_scenario = None, store = False):
        """


        Landscape.build_main(price_curve, multiplier
          [, standard_scenario = None
          [, store = False]]) -> dict()


        Method returns a dictionary showing the size-by-quality surface of
        credit scenarios.

        Method computes the name-specific landscape by multiplying the generic
        leverage data in yield_curve, expressed as price per multiple, by the
        company's specific ``multiplier``.

        Method expects:
         -- ``price_curve`` to be a dictionary of credit price as a function of
            size units that hold constant across companies (e.g., multiples on
            ebitda, revenue, etc.)
         -- ``multiplier`` to be the company-specific size unit (e.g. ebitda)
         -- ``standard_scenario`` to be a CR_Scenario or dictionary

        If ``store`` is True, method saves the surface to instance["size"].

        The surface consists dollar-size keys and CR_Reference values. The
        method uses the standard_scenario as template: all references start with
        only standard scenarios, and then the method adjusts each one per the
        price_curve.

        The method applies the following scenario adjustment algorithm:
         -- set size to normalalized units x multiplier
         -- set price to a leveraged spread over the price_curve mid
            (price goes up for bad scenarios and down for good scenarios)
         -- set structure based on position in the price_curve; as leverage goes
            up, restrictions go from loose to tight
        """
        main_axis = "size"
        main_surface = {}
        #
        working_curve = price_curve.copy()
        working_curve.pop(schema.key_spread)
        working_curve.pop(schema.key_delta_ceiling)
        #make a copy so can modify, then pop out non-numeric keys to sort
        steps = sorted(working_curve.keys())
        step_count = len(steps)
        #
        for i in range(step_count):
            #
            units_of_leverage = steps[i]
            #
            bad_price = pricing_tools.make_bad_price(price_curve, units_of_leverage)
            mid_price = pricing_tools.make_mid_price(price_curve, units_of_leverage)
            good_price = pricing_tools.make_good_price(price_curve, units_of_leverage)
            #
            prices = [bad_price, mid_price, good_price]
            #
            dollar_size = units_of_leverage * multiplier
            dollar_size = round(dollar_size, 6)
            dollar_size = max(0, dollar_size)
            if not standard_scenario:
                mod_scenario = CR_Scenario()
            else:
                mod_scenario = copy.deepcopy(standard_scenario)
            mod_scenario.changeElement("size", dollar_size)
            ref = CR_Reference(standard = mod_scenario)
            #now ref has the same scenario, w the ``scaled`` dollar size, for
            #each quality key
            #adjust ref prices: 
            ref[bad_label].changeElement("price", bad_price)
            ref[mid_label].changeElement("price", mid_price)
            ref[good_label].changeElement("price", good_price)
            #adjust ref structure:
            rank = i/step_count
            if rank < 0.34:
                ref[bad_label].changeElement("structure",1)
                ref[mid_label].changeElement("structure",2)
                ref[good_label].changeElement("structure",3)
            elif rank < 0.68:
                ref[bad_label].changeElement("structure",4)
                ref[mid_label].changeElement("structure",5)
                ref[good_label].changeElement("structure",6)
            else:
                ref[bad_label].changeElement("structure",7)
                ref[mid_label].changeElement("structure",8)
                ref[good_label].changeElement("structure",9)
            main_surface[dollar_size] = ref
            #structure score should be btwn 0 (open)-9 (tight)
            #low leverage lending is loose, higher leverage more constrained
            #the above can be a matrix: [max_percentile: {sc_key: score}...]
        if store:
            self[main_axis] = main_surface
        #
        return main_surface
    
    def forecast(self, ask, field = "size"):
        """


        Landscape.forecast(ask[, field="size"]) -> reference

        
        Method provides a basic forecasting function for a business with a known
        credit landscape.
     
        -- ``field`` must be a key in the instance pointing to a surface
        -- ``ask`` should be a value on the x-axis of the surface
        
        Method delegates all substantive work to the forecast() function in
        Tools.for_pricing_credit. 

        If instance.keep_forecasts is True, method stores the forecast in the
        field.
        """
        surface = self[field]
        result = pricing_tools.forecast(surface, ask)
##        try:
##            result.tag("extrapolated")
##        except AttributeError:
##            pass
        if self.keep_forecasts:
            surface[ask] = result
        return result

    def get_summary(self, padding = None):
        """


        Landscape.get_summary([padding = None]) -> dict


        Method returns a dictionary keyed by fields in self. Each key points to
        a dictionary with a max and min key for that field. For example, if
        instance has a ``price`` key, summary["price"] will show {min = a,
        max = b}.

        For any fields that do not have a sortable set of keys, method lists
        min and max values as None. This applies to fields that themselves have
        a None value. 
        """
        result = {}
        for field in self.keys():
            result[field] = {"lo":padding,"hi":padding}
            try:
                span = sorted(self[field].keys())
                result[field]["lo"] = span[0]
                result[field]["hi"] = span[-1]
            except AttributeError:
                pass
        return result
    
    def label(self, x_axis = "price", y_axis = "size"):
        """


        Landscape.label([x_axis = "price"[, "y_axis" = "size"]]) -> dict


        Method assigns standard, Portal-compatible quality labels to scenarios
        on the x_axis surface. Method assigns labels based on the scenarios'
        value along the y-axis (larger is better). Method returns the updated
        surface.

        The most common application is to label scenarios in a new price
        landscape by their relative quality, as determined by the size of the
        loan that the scenario describes. A company generally prefers to get
        more money then less at a given rate, so the method will assign the
        ``good`` label to the scenario with the largest loan size and the
        ``bad`` label to the scenario with the smallest loan size.

        Algorithm description: 
        Method walks through each reference in the surface. For each reference,
        method sorts the scenarios by their value along the y_axis (for example,
        their "structure" score). Method then assigns the ``bad`` label to the
        scenario with the lowest y-value in the reference, the ``good`` label to
        the one with the highest y-value, and the ``mid`` to the median. 
        """
        surface = self[x_axis]
        #
        for ref in surface.values():
            options = {}
            clean_keys = []
            for k, scenario in ref.items():
                y_value = scenario[y_axis]
                if y_value:
                    try:
                        #check that y_val sorts against numbers
                        mock_list =[y_value, 5, 0.4, 2]
                        mock_list2 = sorted(mock_list)
                        clean_keys.append(y_value)
                    except TypeError:
                        pass
                        #only add sortable std_vals to clean_keys
                options[y_value] = (k, scenario)
            all_keys = list(options.keys())
            if None in all_keys:
                all_keys.remove(None)
##            print("all_keys: ", all_keys)
##            print("clean_keys: ", clean_keys)
            #first, make backup outcomes:
            #do this by assigning good/mid/bad to unsorted keys in all_keys in 
            #whatever pseudo-random order they appear. Theoretically, every ref
            #should contain at least 3 scenarios, and therefore options should
            #contain at least 3 keys. In practice, scenarios may share a value
            #and the number of keys could be as few as 1 (if all scenarios have
            #the same y_val. This could occur, for example, if y_val is a fixed
            #loan term set according to template.
            good_val_key = all_keys.pop()
            mid_val_key = good_val_key
            bad_val_key = good_val_key
            #second, try to actually do real sorting and assign scenarios based
            #on relative size of their keys.          
            ordered = sorted(clean_keys)
            if len(ordered) > 0:
                good_val_key = ordered.pop()
                try:
                    bad_val_key = ordered.pop(0)
                    if bad_val_key in all_keys:
                        all_keys.remove(bad_val_key)
                except IndexError:
                    #IndexError would only come up on ordered.pop, which means
                    #ordered is empty; use a regular key for bad_keys
                    if len(all_keys) > 0:
                        bad_val_key = all_keys.pop(0)
                        #could be that all_keys is the same as clean_keys and
                        #contains only one numeric key
                #reset the default
                mid_val_key = bad_val_key
                if len(ordered) > 0:
                    #ordered should have gotten shorter by now
                    mid_position = max(0,round(len(ordered)/2+0.01)-1)
                    mid_val_key = ordered[mid_position]              
            #each value in options is a (k,scenario) tuple, so pull index #1 to
            #get the actual scenario
            bad_scenario = options[bad_val_key][1]
            mid_scenario = options[mid_val_key][1]
            good_scenario = options[good_val_key][1]
            #now update ref with the correct labels
            ref.changeElement(bad_label, bad_scenario)
            ref.changeElement(mid_label, mid_scenario)
            ref.changeElement(good_label, good_scenario)
            #this part can be a pure dict key write
        #
        return surface
    
    def pivot(self, new_x_axis = "price", new_y_axis = "size", store = False):
        """


        Landscape.pivot([new_x_axis = "price"
          [, new_y_axis = "size" [, store = False]]]) -> dict


        Method constructs a new scenario surface along the new_x_axis and then
        the new_y_axis from the data points in each of the existing surfaces.

        #builds 3-d surfaces: scenarios as a function of (x, y):
           #scenarios as a function of x
           #references as a function of y
        
        #REF_SCAPE is now always instance
        
        #ALWAYS goes through every surface in instance; will build new landscape from "by_term", "by_fit", etc.
            #if you want to limit this scope, remove keys manually?
        #MOST COMMON OPERATION: flip landscape keyed by size into one keyed by price <--------------------------------------------------------------------------
        #overwrites old data on ``store``
        #vars should probably be called "new_x_axis", "new_y_axis"

        Method goes through each reference point in ref_scape. For each scenario
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

        To assign scenarios in a landscape to standard quality keys, run
        Landscape.label().
        """
        new_surface = {}
        #
        for existing_surface in sorted(self.values()):
            #sort existing keys to ensure stable order and output
            for scenario in existing_surface.values():
                new_x_value = scenario[new_x_axis]
                #in the size-to-price landscape transform, x_value would be the
                #price for the loan size that scenario describes
                #
                new_y_value = scenario[new_y_axis]
                #in the size-to-price landscape transform, y_value would be the
                #size of the loan in the scenario.
                #
                if new_x_value not in new_surface.keys():
                    new_ref = CR_Reference()
                    #the reference is going to store a bunch of scenarios, keyed
                    #by y-value
                    new_ref.setAll(new_x_axis, new_x_value)
                    #hold the x_value constant across all scenarios in the ref
                    new_surface[new_x_value] = new_ref
                #
                new_surface[new_x_value][new_y_value] = scenario
                #
        if store:
            self[new_x_axis] = new_surface
        #
        return new_surface
        #
        #this method pulls data from all price surfaces in the instance. 
        #accordingly, we have to pull the y_value explicitly here. since python
        #dictionaries do not guarantee key order, we do not know which surface
        #we are walking at any given cycle of the loop. all we know is how to
        #transform data points on that surface into the data points we need. for
        #example, we could be walking a surface keyed by loan term (in months).
        #we should still key all of its scenarios by their price and then by
        #their size.
        #
        #the situation where the instance has only one surface, keyed by size,
        #then by price, and we want to create a price-based landscape is a
        #special case. there, references  on the only existing_surface are
        #already keyed by the new_y_value we want. in this one situation,
        #pulling the new y value explicitly can seem redundant.
        
    def trim(self, field, lo_bound=None, hi_bound=None):
        """


        Landscape.trim(field, lo_bound=None, hi_bound=None) -> None


        For specified field in landscape, method deletes items w keys smaller
        than the lo_bound or larger than the hi_bound. 
        """
        old = self.keep_forecasts
        self.keep_forecasts = True
        if lo_bound:
            ref_lo = self.forecast(ask=lo_bound, field=field)
        if hi_bound:
            ref_hi = self.forecast(ask=hi_bound, field=field)
        F = self[field]
        points = sorted(F.keys())
        for p in points:
            if lo_bound and (p < lo_bound):
                F.pop(p)
            elif hi_bound and (p > hi_bound):
                F.pop(p)
        self.keep_forecasts = old
