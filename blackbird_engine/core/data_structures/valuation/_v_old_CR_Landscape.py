#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Valuation.CR_Landscape
"""

Module defines CR_Landscape class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class CR_Landscape    template for credit landscape objects (reference values)
====================  ==========================================================
"""




#imports
from . import Parameters

from .Pattern import Pattern




#globals
#n/a

#classes
class CR_Landscape(Pattern):
    """

    Class provides a dict-like container for tracking credit landscapes.
    Container has standard fields specified in ``fields_CR_Landscape`` global in
    this module.

    Each key should point to a dictionary where values are CR_References.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    keepForecasts         bool, if True, forecast() adds extrapolated
                          references to self.
    
    FUNCTIONS:
    averageReferences()   takes two references, returns a new one w avg values
    forecast()            returns a reference for a price or size ask
    getSummary()          returns dict w min & max values for each field
    updateLabels()        method reviews all scenarios and selects bad,mid,good
    ====================  ======================================================
    """
    def __init__(self,name = "Pattern",standard = None):
        Pattern.__init__(self,name)
        self.keepForecasts = True
        self.trackChanges = True
        self.fromkeys(Parameters.fields_CR_Landscape)
        self.applyStandard(standard)

    def averageReferences(self,aSc,bSc,aWeight = 1, bWeight = 1):
        """

        Landscape.averageRefereces(aSc,bSc) -> mSc
        
        Method generates an ``average`` reference (mSc) from two others. The
        average reference has all of the keys shared by a and b. Values in mSc
        are:
        
        -- an averageReference, if the key's value in a is a dict-type obj
        -- the arithmetic mean of a[k] and b[k], if it's possible to compute
        -- a[k] (in all other cases).
        
        Method accepts any reference object that is descended from a dictionary.
        Method returns a new object of the same class as reference a.

        aWeight and bWeight are optional multipliers that allow the method to
        compute weighted averages. 
        """
        mSc = aSc.__class__()
        sharedKeys = zip(aSc.keys(),bSc.keys())
        for ks in sharedKeys:
            #ks is a tuple where each element is itself a tuple that repeats the
            #shared key 2x
            k = ks[0]
            aVal = aSc[k]
            bVal = bSc[k]
            mVal = None
            if dict().__class__ in aVal.__class__.__mro__:
                mVal = self.averageReferences(aVal,bVal,aWeight,bWeight)
            else:
                try: 
                    aVal = aVal * aWeight
                    bVal = bVal * bWeight
                    mVal = (aVal+bVal)/2
                    mVal = round(mVal,6)
                except TypeError:
                    mVal = aVal
            mSc[k] = mVal
        return mSc
        #NOTE: Method assumes that a reference contains either numeric values OR
        #dict / pattern objects, NOT lineItems. 
        #
        #can expand this method to take in arbitrarily many references:
        #def avg_ref(self,*references):
            #keys = [x.keys() for x in references]
            #sharedKeys = zip(*keys)
            #for ks in sharedKeys:
                #k = ks[0]
                #subRefs = [x[k]] for x in references]
                #if dict().__class__ in subRefs[0].__class__.__mro__:
                    #mVal = self.averageReferences(subRefs)
                #else:
                    #try:
                        #mval = sum(subRefs)/len(subRefs)
                    #else:
                        #mval = subRefs[0]
                #mSc[k] = mval
            #return mSc
        
    def forecast(self,ask = None, field = "size"):
        """

        Landscape.forecast(ask=None[,field="size"]) -> reference
        
        Method provides a basic forecasting function for a business with a known
        credit landscape. Method takes either a price or size ask (but not both)
        and tries to find the best-matching reference.

        This reference is either:
         -- a pre-recorded value, or
         -- an extrapolated value

        The method returns pre-recorded references when the ask is one of the
        keys to the relevant part (size or price) of the landscape. The method
        also returns a pre-recorded reference when the ask is either less than
        the smallest key (returns the min key's reference) or larger than the
        largest key specified (returns the max key's reference).

        If the ask is between the smallest and largest specified key, the method
        generates a new reference. It does so by calling averageReferences() on
        the two values whose keys are closest to the ask.

        If instance.keepForecasts is True, method adds the resulting reference
        to  self. 
        """       
        result = None
        if field not in self.keys():
            label = "fixed variable not in landscape keys"
            raise Exception(label)
        if not ask:
            label = "must specify ask"
            raise Exception(label)
        #check if ask is within known range
        options = self[field]
        known_vals = sorted(options.keys())
        print("known_vals: ", known_vals)
        if ask in known_vals:
            result = options[ask]
        else:
            lo = known_vals[0]
            hi = known_vals[-1]
            if ask < lo:
                pass
                #keep result as None
                #or can set to a Note:
                #result = CR_Reference()
                #comment = "too  small" 
                #result.changeElement("note",comment)
            elif ask > hi:
                pass
                #keep result as None
            else:
                #ask in known range but not specified, so need to extrapolate the
                #reference. do so by finding first value larger than ask. then
                #average that value with its smaller neighbor. 
                i_less = None
                i_more = None
                less_wgt = 1
                more_wgt = 1
                for i in range(len(known_vals)):
                    val = known_vals[i]
                    if val < ask:
                        continue
                    else:
                        i_more = i
                        more_wgt = ask/val
                        break
                #should always find i_more before continuing. otherwise, ask either
                #equals or exceeds the upper boundary, both of which tested negative 
                i_less = i_more-1
                less_wgt = ask/known_vals[i_less]
                b = options[known_vals[i_more]]
                a = options[known_vals[i_less]]
                result = self.averageReferences(a,b,less_wgt,more_wgt)
                try:
                    result.tag("extrapolated")
                except AttributeError:
                    pass
                if self.keepForecasts:
                    try:
                        options.addElement(ask,result)
                    except AttributeError:
                        options[ask] = result
        return result

    def getSummary(self,padding = None):
        """

        Landscape.getSummary([padding = None]) -> dict

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

    def updateLabels(self,subscape = None,std_var = "size"):
        """

        CR_Landscape([subscape = None[,std_var="size"]) -> subscape

        Method expects subscapes to be dictionaries of k:refs.

        If subscape = None, method goes through self.price.

        Method goes through each reference in the subscape. For each reference,
        method organizes all of its scenarios by their value for std_var
        (for example, their "structure" score). Method then sets the scenario
        with the lowest standard value as bad, the highest as good, and the
        median as mid.

        Method returns the updated subscape object.

        NOTE: Method changes the subscape in place. 
        """
        if not subscape:
            subscape = self.price
        bad = Parameters.fields_CR_Reference[0]
        mid = Parameters.fields_CR_Reference[1]
        good = Parameters.fields_CR_Reference[2]
        for ref in subscape.values():
            options = {}
            clean_keys = []
            for k,scenario in ref.items():
                print("k: ",k)
                std_val = scenario[std_var]
                print("std_val: ",std_val)
                if std_val:
                    try:
                        mockL =[std_val,5,0.4,2]
                        mockL2 = sorted(mockL)
                        clean_keys.append(std_val)
                    except TypeError:
                        pass
                    #only add sortable std_vals to clean_keys
                options[std_val] = (k,scenario)
            all_keys = list(options.keys())
            if None in all_keys:
                all_keys.remove(None)
            print("all_keys: ", all_keys)
            print("clean_keys: ", clean_keys)
            #first, make backup outcomes:
            #do this by assigning good/mid/bad to unsorted keys in all_keys in 
            #whatever pseudo-random order they appear. Theoretically, every ref
            #should contain at least 3 scenarios, and therefore options should
            #contain at least 3 keys. In practice, scenarios may share a value
            #and the number of keys could be as few as 1 (if all scenarios have
            #the same std_val. This could occur, for example, if std_val is a
            #template term.
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
            #each value in options is a (k,scenario) tuple, so use subscript to
            #get the actual scenario
            bad_scenario = options[bad_val_key][1]
            mid_scenario = options[mid_val_key][1]
            good_scenario = options[good_val_key][1]
            #now update ref with the correct scenarios
            ref.changeElement(bad,bad_scenario)
            ref.changeElement(mid,mid_scenario)
            ref.changeElement(good,good_scenario)
        return subscape
