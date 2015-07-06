#completion rules
#completely stateless
#

def quality_only(item):
    complete = False
    #
    standard = item.guide.quality.standard
    if item.guide.quality.current >= standard:
        complete = True
    #
    return complete

def quality_and_attention(item):
    complete = False
    #
    quality_cap = item.guide.quality.standard
    attention_cap = item.guide.attention.budget
    #
    worked_out = False
    asked_out = False
    #
    if item.guide.quality.current >= quality_cap:
        worked_out = True
    if item.guide.attention.current >= attention_cap:
        asked_out = True
    #
    if any(worked_out, asked_out):
        complete = True
    #
    return complete
