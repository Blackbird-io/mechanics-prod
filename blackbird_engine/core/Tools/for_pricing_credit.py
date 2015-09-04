#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Tools.for_pricing_credit
"""

Module defines functions for computing credit prices in standalone, CR_Scenrio,
and CR_Reference forms. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
average_references()  takes two references, returns a new one w avg values
forecast()            returns a reference for a value on surface x axis

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a



#globals
#n/a

#functions
def average_references(a_ref, b_ref, a_weight = 1, b_weight = 1):
    """


    average_references(a_ref, b_ref[, a_weight = 1[, b_weight = 1]]) -> obj


    Function generates an ``average`` reference (m_ref) from two others. The
    average reference has all of the keys shared by a and b. Values in m_ref
    are:

    -- an average_reference, if the key's value in a is a dict-type obj
    -- the arithmetic mean of a[k] and b[k], if it's possible to compute
    -- a[k] (in all other cases).

    Function accepts any reference object that is descended from a dictionary.
    Function returns a new object of the same class as reference a.

    a_weight and b_weight are optional multipliers that allow the method to
    compute weighted averages.
    """
    #
    m_ref = a_ref.__class__()
    #
    shared_keys = set(a_ref) & set(b_ref)
    for k in shared_keys:
        a_val = a_ref[k]
        b_val = b_ref[k]
        m_val = None
        if dict().__class__ in a_val.__class__.__mro__:
            m_val = average_references(a_val, b_val, a_weight, b_weight)
        else:
            try: 
                a_val = a_val * a_weight
                b_val = b_val * b_weight
                m_val = (a_val + b_val)/2
                m_val = round(m_val,6)
            except TypeError:
                m_val = a_val
        m_ref[k] = m_val
    #
    return m_ref
    #NOTE: Method assumes that a reference contains either numeric values OR
    #dict / pattern objects, NOT lineItems. 
    #
    #can expand this method to take in arbitrarily many references:
    #def avg_ref(*references):
        #keys = [x.keys() for x in references]
        #sharedKeys = zip(*keys)
        #for ks in sharedKeys:
            #k = ks[0]
            #subRefs = [x[k]] for x in references]
            #if dict().__class__ in subRefs[0].__class__.__mro__:
                #mVal = average_references(subRefs)
            #else:
                #try:
                    #mval = sum(subRefs)/len(subRefs)
                #else:
                    #mval = subRefs[0]
            #mSc[k] = mval
        #return mSc

def forecast(surface, x_val):
    """


    forecast(surface, x_val) -> CR_Reference
    
    
    Function returns a reference for a value on the surface's x-axis. If surface
    already includes ``x_val``, function pulls the reference associated with
    that value. Otherwise, function creates a new reference from the two known
    points closest to x_val.
    """
    #right now, function averages two closest data points. can turn into a line
    #of best fit analysis. 
    result = None
    #
    known_vals = sorted(surface.keys())
    if x_val in known_vals:
        result = surface[x_val]
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
                if val < x_val:
                    continue
                else:
                    i_more = i
                    more_wgt = x_val/val
                    break
            #should always find i_more before continuing. otherwise, ask either
            #equals or exceeds the upper boundary, both of which tested negative 
            i_less = i_more - 1
            less_wgt = x_val/known_vals[i_less]
            b = surface[known_vals[i_more]]
            a = surface[known_vals[i_less]]
            result = average_references(a, b, less_wgt, more_wgt)
    #
    return result
    
def make_high_price(price_curve, units_of_leverage):
    spread = price_curve[schema.key_spread]
    mid = make_mid_price(price_curve, units_of_leverage)
    adj = spread * units_of_leverage
    p = mid + adj
    p = round(p, 6)
    #
    return p

def make_low_price(price_curve, units_of_leverage):
    """
    doesn't change the price curve
    """
    mid = make_mid_price(price_curve, units_of_leverage)
    spread = price_curve[schema.key_spread]
    delta_ceiling = price_curve[schema.key_delta_ceiling]
    #
    adj = spread * units_of_leverage
    adj = min(adj, delta_ceiling)
    p = mid - adj
    p = round(p, 6)
    #
    return p

def make_mid_price(price_curve, units_of_leverage):
    p = price_curve[units_of_leverage]
    p = round(p, 6)
    #
    return p


