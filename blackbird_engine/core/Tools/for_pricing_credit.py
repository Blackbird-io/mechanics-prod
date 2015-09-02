#imports
from DataStructures.Valuation import schema



#globals


#pricing tools

def make_high_price(price_curve, units_of_leverage):
    spread = price_curve[schema.key_spread]
    mid = make_mid_price(price_curve, units_of_leverage)
    adj = spread * units_of_leverage
    p = mid + adj
    p = round(p, 6)
    #
    return p

def make_mid_price(price_curve, units_of_leverage):
    p = price_curve[units_of_leverage]
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
