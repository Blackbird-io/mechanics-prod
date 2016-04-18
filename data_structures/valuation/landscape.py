#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.valuation.landscape
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
Landscape             template for credit landscape objects (reference values)
====================  ==========================================================
"""




#imports
import copy

from tools import for_pricing_credit as pricing_tools

from . import parameters

from .cr_reference import CR_Reference
from .cr_scenario import CR_Scenario

from ..guidance.step import Step




#globals
bad_label = parameters.fields_CR_Reference[0]
mid_label = parameters.fields_CR_Reference[1]
good_label = parameters.fields_CR_Reference[2]

#classes
class Landscape(dict, Step):
    """

    Class provides a dict-like container for building and storing surfaces of
    market outcomes. Each surface is a dictionary that stores CR_Reference
    objects populated with credit scenarios. We can think of the keys for the
    surface as the x-axis and the keys for the reference as the y-axis. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    keep_forecasts        bool, if True, keep forecasts.
    
    FUNCTIONS:
    build_main()          construct size-based surface from price curve
    combine()             combine datapoints from multiple surfaces
    enrich()              add some datapoints from one surface to another
    forecast()            returns a reference for a price or size ask
    get_summary()         returns dict w min & max values for each field
    label()               select scenarios in surface that are bad/mid/good
    pick_best()           select surface with ``best`` values for an axis
    pivot()               organize data in surface along new axes
    sort()                arrange surfaces from worst to best along an axis
    trim()                cuts off ref points outside an external range
    ====================  ======================================================
    """
    def __init__(self, name = None):
        dict.__init__(self)
        Step.__init__(self, name)
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
        working_curve.pop(parameters.key_spread)
        working_curve.pop(parameters.key_delta_ceiling)
        #make a copy so can modify, then pop out non-numeric keys to sort
        steps = sorted(working_curve.keys())
        step_count = len(steps)
        #
        for i in range(step_count):
            #
            units_of_leverage = steps[i]
            #
            bad_price = pricing_tools.make_price("high", price_curve, units_of_leverage)
            mid_price = pricing_tools.make_price("mid", price_curve, units_of_leverage)
            good_price = pricing_tools.make_price("low", price_curve, units_of_leverage)
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
    
    def combine(self, surfaces, x_axis = "size", y_axis = "price", y_delta = 0.04):
        """


        Landscape.combine() -> dict


        Method combines datapoints from multiple surfaces into a new surface
        aligned on the specified axes. Result is unlabelled.
        """        
        result = None
        #
        stack = self.sort(surfaces, scoring_axis = y_axis)
        result = copy.deepcopy(stack[0])
        #
        for i in range(1, len(stack)):
            neighbor = stack[i]
            aligned = self.pivot(neighbor, x_axis, y_axis)
            result = self.enrich(result, neighbor, y_delta)
        #
        return result               
        
    def enrich(self, main_surface, other_surface, y_delta , extend = True):
        """


        Landscape.enrich(main_surface, other_surface,
          y_delta = 0.04, extend = True]) -> main_surface


        Method populates main_surface with data points from other_surface.
        For any x-axis value on the other surface, method picks up data points
        whose y-value falls within ``y_delta`` of the corresponding y-value on
        the main surface. Method then adds copies of these datapoints to the
        main surface.

        If ``extend`` is True, method will also add data points for any
        ``other_surface`` x that falls outside the x-value range covered by
        ``main_surface``. Method will skip these out-of-range points if
        ``extend`` is False

        Method expects main_surface and other_surface to align along both axes.

        Sample Use Case: Talladega Fruit Company (``TFC``)

        Blackbird has modelled operations and financial results at TFC. TFC has
        some unencumbered hard assets (refridgeration and warehousing facilities)
        worth $20mm. TFC also generates $10mm a year of EBITDA. As a result, TFC
        faces 2 distinct credit environments: the company can borrow up to 80%
        of its hard-asset value from a bank in the form of a cheap ABL loan. TFC
        can also borrow up to 5x EBITDA from a fund on a leveraged basis. The
        ABL loans all range from 2.00% to 5.00% WACD. Leveraged loans range from
        6% to 20% WACD, and start at $2mm in size.

        The TFC model carries both of these landscapes on its valuation record.
        Blackbird built both landscapes from price curves, so each exists along
        the size-price axes. The FTC model has no other landscapes. 

        Blackbird now has to generate a ``global`` credit landscape for the
        company. To do so, Blackbird will use Landscape.enrich() to pull in some
        of the expensive data from the LL landscape onto a copy of the ABL one.

        The enrichment process follows two guidelines. First, all things being
        equal, a rational borrower will always prefer a cheaper loan to a more
        expensive one at the same size. The option to borrow $8mm at 9% is not
        a real option when TFC can also borrow the same $8mm at 4.5%.

        Second, individual institutions make their own lending decisions
        independently, so even if **some** bank can loan 80% LTV to TFC at
        4.50%, there is no guarantee that TFC will find such a bank, either on
        Blackbird or elsewhere. Accordingly, TFC may end up seeing only the
        more expensive LL quote when it goes to look for $8mm.

        In such an event, TFC may rationally transact at a price higher than the
        one that exists in the best (most favorable) market. TFC may choose the
        more expensive fund loan even when the company knows a cheaper ABL
        alternative should be available. The company will do so when it thinks
        its unlikely to find the cheap ABL lender, or the search is not worth
        its time. 

        We can balance these considerations by assuming that the probability of
        the company taking a loan from a more expensive market (surface) is
        inversely proportional to the difference in price between the surfaces.
        When the difference is high, TFC will keep searching. When the
        difference is low, TFC may settle for what's in front of it.

        When builindg a global landscape through enrich(), we can reflect these
        considerations by defining a ``y_delta`` within which we expect TFC to
        seriously consider all offers. So if our y_delta is 4%, we are saying
        that TFC may actually take a loan that's 4% more expensive than the
        theoretical best outcome. Beyond that spread, the company will keep
        looking. The y_delta analysis applies only to situations where the same
        amount of debt can come from two distinct markets. If the size is large
        enough, say $35mm, such that the loan only exists on the LL surface,
        y_delta reasoning doesn't apply. Here. ``extend`` = True will pick up
        the LL quote as-is.        
        """
        x_lo_bound = 0
        x_hi_bound = 0
        if main_surface:
            x_lo_bound = min(main_surface)
            x_hi_bound = max(main_surface)
        #
        for (x, new_ref) in other_surface.items():
            #unsorted pseudo-RANDOM order
            if x_lo_bound <= x <= x_hi_bound:
                #
                base_ref = forecast(main_surface, x, store = True)
                #store the forecast to make sure main[x] is a valid call later
                y_hi_bound = max(base_ref) + y_delta
                y_lo_bound = min(base_ref) - y_delta
                for (y, new_scenario) in new_ref:
                    if y_lo_bound <= y <= y_hi_bound:
                        main_surface[x][y] = new_scenario.copy()
                        #we know that main_surface[x] exists because the
                        #forecast() call above created it if the key wasn't
                        #there before
                    else:
                        pass
            else:
                if extend:
                    main_surface[x] = copy.deepcopy(new_ref)
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
            except (AttributeError, IndexError) as e:
                pass
        return result
    
    def label(self, surface = None, x_axis = "price", y_axis = "size"):
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
        if not surface:
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

    def pick_best(surfaces, scoring_axis = "price",
                  lower_is_better = True, sort = True):
        """


        Landscape.pick_best(surfaces
          [, scoring_axis = "price"
          [, lower_is_better = True
          [, sort = True]]]) -> (best_surface, runners_up)


        Method selects an object from ``surfaces`` in which a standard query
        generates the best value along the ``scoring_axis``. Method returns a
        tuple of (i) the best surface and (ii) a list of the runners up, sorted
        by size. 

        If ``lower_is_better`` is True, method will choose the lowest value as
        the best. Otherwise, method will choose the highest value as the best.

        If ``sort`` is True, method will sort the surfaces before picking one
        from which to choose the standard query. The objects in ``runners_up``
        retain this order. Accordingly, you can set ``sort`` to ``False`` when
        running the function recursively to preserve processing cycles.

        Method assumes ``surfaces`` align on the same x_axis. 

        Algorithm:
        (1) choose the surface with the smallest max size (x value)
        (2) set that max x-value as the standard query
        (3) get a forecast for the standard query on every surface
        (4) find the ``best`` scoring_axis value in the forecast's scenarios
        (5) store the surface under the best scoring value
        (6) select the surface with the best scoring value globally
        """
        best_surface = None
        runners_up = None
        #
        choose = max
        if lower_is_better:
            choose = min
        if sort:
            by_size = sorted(surfaces, key = lambda x: max(x))
        else:
            by_size = surfaces[:]
        standard_surface = by_size[0]
        standard_query = max(standard_surface)
        #
        #here, we choose the surface whose x axis ends with the smallest value
        #as our standard (``lowest``) surface. we then pick a standard x value
        #from that surface. we will score surfaces based on how their outputs
        #along the scoring_axis for our standard x value. this selection logic
        #depends on the standard value falling within the bounds of each
        #surface (otherwise, the surface won't be able to return a reference we
        #can compare). accordingly, we use the max x-value from the lowest
        #surface, on the assumption that it's the number that's most likely to
        #fit into other x axes.
        #
        #we can improve this function by querying the surfaces across multiple
        #shared datapoints. we could then score the surfaces along their average
        #result or even their slope. implementation would depend on finding
        #an overlapping range. 
        #
        #the slope calculation could be a (f(max x) - f(min x)/(max x - min x)
        #or something more involved, such as a d(y)/d(x) for all datapoints.
        #
        quotes = {}
        for i in range(len(by_size)):
            surface = by_size[i]
            ref = forecast(surface, smallest_upper_limit)
            scores = [scenario[scoring_key] for scenario in ref.values()]
            best_score_in_ref = choose(scores)
            #since the order of ref values is pseudo-random, the scenario that
            #generates the best score may differ from run to run. for example,
            #if scoring_axis is "structure" and scenarios A and B both have a
            #score of 8, their 8's will appear at different positions in
            #``scores`` every time we run the routine. this will occur because
            #the order of scores matches the order of scenarios, and python
            #stores scenarios (dict values) in a pseudo-random order.
            #
            #the randomness is ok here because we care only about the magnitude
            #of the best score, not the specific scenario where that score
            #occurs.
            #
            #if we move the selection logic to one that looks at a scenario
            #more whollistically, we would need to move to a stable evaluation
            #order to avoid getting randomized results. 
            quotes[best_score_in_ref] = (i, surface, ref)
        #
        #this method **ignores** a surface's y-axis by looking deeper, right
        #into each scenario's z-score (value on the scoring_axis). for example,
        #if the scoring_axis is ``structure``, the method will score a surface
        #based on its output's best ``structure`` value. since the function
        #walks through each scenario in the forecasted reference, its output
        #is the same regardless of how the reference keys its scenarios in the
        #the first place (i.e., the surface's y-axis). 
        #
        best_score_overall = choose(quotes.keys())
        best_surface = quotes[best_score][1]
        i_best = quotes[best_score][0]
        by_size.pop(i_best)
        #pull out winner, keep the runners up
        runners_up = by_size
        return (best_surface, runners_up)
    
    def pivot(self, sources = None, new_x_axis = "price",
              new_y_axis = "size", store = False):
        """


        Landscape.pivot(sources = None, [new_x_axis = "price"
          [, new_y_axis = "size" [, store = False]]]) -> dict


        Method assembles the data points in each of the ``sources`` into a new
        surface along the ``new_x_axis`` and ``new_y_axis``.

        -- ``sources`` should be an iterable container. If left blank, method
           goes through each surface in the instance.
        -- ``new_x_axis`` should be a key in each of the scenarios.
        -- ``new_y_axis`` should also be a key in each of the scenarios.

        If ``store`` is True, method will set instance[new_x_axis] to the new
        surface.
        
        A common use case is to flip a surface keyed by loan size, where for
        each size references list different price and/or quality outcomes, into
        a new surface keyed by price-then-size.

        NOTE: Method does **not** label scenarios as "bad","good", etc.

        To assign scenarios to a new surface, run Landscape.label().
        """
        new_surface = {}
        if not sources:
            ordered_keys = sorted(self.keys())
            sources = [self[k] for k in ordered_keys]
        #
        for existing_surface in sources:
            #sort existing keys to ensure stable order and output
            for reference in existing_surface.values():
                #values on the surface are references, keyed by either quality
                #labels and/or some other axis
                for scenario in reference.values():
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
        
    def sort(surfaces, scoring_axis = "price",
             lower_is_better = True, reverse = False):
        """


        Landscape.sort(surfaces,
            [scoring_axis = "price"[, lower_is_better = True]]) -> list


        Method organizes objects in ``surfaces`` into a list by their relative
        quality along the ``scoring_axis``. Method returns a list from worst
        (lowest score) to best (highest score). If ``reverse`` is True, method
        returns a list from best to worst.

        Method expects surfaces to share an x-axis. Method delegates selection
        work to Landscape.pick_best() and iterates through remainder until there
        is nothing left.
        """
        result = []
        best, remainder = self.pick_best(surfaces, scoring_axis, lower_is_better)
        result.append(best)
        while remainder:
            if len(remainder) == 1:
                best = remainder.pop()
            else:
                best, remainder = self.pick_best(remainder, scoring_axis,
                                                 lower_is_better, sort = False)
                #old remainder is already sorted by the scoring_axis from prior
                #runs. save cycles by skipping the repeated sort.
            result.append(best)
        #
        if not reverse:
            result = result[::-1]
        #
        return result

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

