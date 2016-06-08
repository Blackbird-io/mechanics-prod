# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: tools.for_pricing_credit

"""

Module defines functions for computing credit prices. Functions usually rely on
a price curve that defines cost of capital for a known number of units (turns
on EBITDA, turns on revenue, etc.).
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
average_references()  takes two references, returns a new one w avg values
forecast()            returns a reference for a value on surface x axis
make_price()          compute price from curve, for given quality
price_low()           compute low price for units on curve
price_mid()           compute high price for units on curve
price_high()          compute mid price for units on curve

CLASSES:
n/a
====================  ==========================================================
"""




#imports
from data_structures.valuation import parameters




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

def forecast(surface, x_val, fill_edge = True):
    """


    forecast(surface, x_val) -> CR_Reference
    
    
    Function returns a reference for a value on the surface's x-axis.

    The surface is usually a dict-type object that represents a matrix (2+ 
    dimensional array) of scenario objects. If surface already includes
    ``x_val``, function pulls the reference associated with that value.
    Otherwise, function creates a new reference from the two known points
    closest to x_val.

    If ``fill_edge`` is True, function will return the closest edge case when
    ``x_val`` falls outside the [min, max] range for the surface x-axis.
    Otherwise, function will return None for out-of-bounds asks. 
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
        if x_val < lo:
            if fill_edge:
                result = surface[lo]
            else:
                pass
            #add a comment #<------------------------------------------------------------------------------------fix!
            #or can set to a Note:
            #result = CR_Reference()
            #comment = "too  small" 
            #result.changeElement("note",comment)
        elif x_val > hi:
            if fill_edge:
                result = surface[hi]
            else:
                pass
            #add a comment #<------------------------------------------------------------------------------------fix!
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
    
def price_high(price_curve, units_of_leverage):
    """


    make_high_price(price_curve, units_of_leverage) -> float


    Function returns the mid price increased by the cumulative turn-based
    spread.
    """
    spread = price_curve[parameters.key_spread]
    mid = price_mid(price_curve, units_of_leverage)
    adj = spread * units_of_leverage
    p = mid + adj
    p = round(p, 6)
    #
    return p

def price_low(price_curve, units_of_leverage):
    """


    make_low_price(price_curve, units_of_leverage) -> float


    Function returns the mid price decreased by the smaller of (i) cumulative
    turn-based spread, or (ii) the curve's delta_ceiling. Function also makes
    sure the price clears the credit_price_floor defined in Globals.
    """
    mid = price_mid(price_curve, units_of_leverage)
    spread = price_curve[parameters.key_spread]
    delta_ceiling = price_curve[parameters.key_delta_ceiling]
    #
    adj = spread * units_of_leverage
    adj = min(adj, delta_ceiling)
    p = mid - adj
##    p = max(p, Globals.credit_price_floor) #<--------------------------------------------------------------------------------- implement me!
    p = round(p, 6)
    #
    return p

def price_mid(price_curve, units_of_leverage):
    """


    make_low_price(price_curve, units_of_leverage) -> float


    Function returns the mid price decreased by the smaller of (i) cumulative
    turn-based spread, or (ii) the curve's delta_ceiling. Function also makes
    sure the price clears the credit_price_floor defined in Globals.
    """
    p = price_curve[units_of_leverage]
    p = round(p, 6)
    #
    return p

def make_price(level, price_curve, units_of_leverage):
    """


    make_price(level, price_curve, units_of_leverage) -> float


    Function returns the unit-based price for leverage. Delegates all work
    to level-appropriate subroutines. 
    """
    routines = {"mid" : price_mid,
                "low" : price_low,
                "high" : price_high}
    routine = routines[level]
    p = routine(price_curve, units_of_leverage)
    #
    return p
