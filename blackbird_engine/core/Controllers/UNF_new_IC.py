#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.new_IC

"""


====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

====================  ==========================================================
"""



#imports
from . import completion_rules

from .level import Level




#globals
protocols = dict()
protocols[0] = "Walk through path items with priority > 0 in existing order."
protocols[1] = "Organize path into priority levels, then walk through each level in order."
protocols[2] = "Same as 1, but stop when attention runs out."
##protocols[3] = "Stop working on an item when it runs out of attention budget or reaches min quality."
##p3 first allocates available attention to open items. first, based on need, then based on cap. first
#to high level priority, then on down. then goes through and does a more complex check on completion.
#so basically, if you have too many open items you will run out of attention quickly.
#
#only allocate based on cap if need in excess of cap. so basically dont get to later items if go
#too deep early. 
#


##attention tracking: 
## - model has to keep fixed attention budget
## - someone has to tick up used attention for each question for the model as a    whole
## - ??someone has to tick up attention for each focal point??
##     may not be necessary to measure attn for each item if we measure attention in      the same units as quality
##     ex: cost.attn.current = 3, cost.quality.current = 1,
##	what to do? 
##	#kind of odd, ive incurred a cost of 3 (questions) and only got quality of 	1
##     ex: labor.attn.current = 1, labor.quality.current = 2
##	#
##	#every time an MQ_ goes up, up_controller should increment attention on         the focal point by the question's attention cost, which can initially
##        be 1 but go up based on number of elements. 

## alternatively, could change the quality thing to a single quality        requirement. so would have minStandard only. at every iteration, see how much quality you still have to put in, vs how much attention you have left for budget. 


#classes
class InterviewController(Controller):
    """

    IC objects establish the focal point for an interview.

    process() delegates to protocol-specific routine. process() provides unpack, wrap, and other shared elements.
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _known_protocols
    _protocol
    MR                    instance of Messenger class

    FUNCTIONS:
    prioritize()          orders path into a bunch of priority levels
    process()             in MQR message, sets model focal point
    set_progress()        sets progress bar
    wrap_interview()      ????
    
    ====================  ======================================================
    """
    #class vars    
    def __init__(self):
        self._protocol = 1

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if value in self._protocol_routines:
            self._protocol = value
        else:
            c = "Unknown protocol. Attribute accepts only known keys for protocol routines."
            raise ManagedAttributeError(c)
    
    def process(self, mqr):
        """
        first, if model already has a focal point, check if IC should keep this
        focal point. otherwise, find new focal point through routine. 
        """
        #
        fp = None
        Controller.process(self, msg)
        #
        model = self.MR.activeModel
        #
        #check known focal point
        old_fp = model.interview.focal_point
        known_rule = model.interview.completion_rule
        if known_rule:
            if not known_rule(old_fp):
                fp = old_fp
                #rule says that old_fp is not yet complete. keep fp constant.
        if not fp:
            #
            #get here when model either: (1) doesn't have a focal point, (2)
            #doesnt have a known rule for testing the focal point, or (3) the 
            #known focal point satisfies the known rule and Blackbird needs to
            #find a new one.
            #
            routine = self._protocol_routines[self.protocol]
            #find and apply the protocl-specific processing routine. IC stores
            #routines as class methods, so need to pass in the instance
            #explicitly.
            #
            fp = routine(self, model)
        if not fp:
            model.interview.reset_cache()
            fp = routine(self, model)
            #if protocol routine doesnt find a focal point, reset cache and
            #try again. dont want to finish prematurely.
        #
        if not fp:
            new_mqr = self.wrap_interview()
        else:
            self.set_progress(model)
            new_mqr = self.wrap_to_point()
        #
        return new_mqr

    def prioritize_single(self, container):
        """
        """
        levels = dict()
        single_level = Level()
        levels[Globals.priority_max] = single_level
        for item in container.items():
            if not item.guide.priority.current:
                continue
            else:
                single_level.append(item)
        #
        return levels

    def prioritize_multi(self, container):
        """
        """
        levels = dict()
        for item in container.items:
            if not item.guide.priority.current:
                #skip 0-priority items
                continue
            else:
                p = item.guide.priority.current
                peer_level = levels.setdefault(p, Level())
                peer_level.append(p)
        #
        return levels                

    def focus(self, model, selector):
        fp = None
        levels = model.interview.levels
        #go through levels most to least important
        for level in priorities:
            if level.complete:
                continue
            else:
                fp = selector(level, model)
                if fp:
                    break
                else:
                    level.complete = True
                    continue
        #
        return fp

    def selector_quality(self, level, model):
        fp = None
        #
        rule = completion_rules.quality_only
        model.interview.set_completion_rule(rule)
        #
        remaining = range(level.last, len(level))
        for i in remaining:
            item = level[i]
            if rule(item):
                item.guide.complete = True
                continue
            else:
                #if item is not complete
                item.guide.complete = False
                fp = item
                level.last = i
                break
        #
        return fp

    def selector_attention_breadth(self, level, model):
        #
        #if level need exceeds availability, spreads available attention over the entire priority level. otherwise
        #runs vanilla quality 
        #
        fp = None
        #
        rule = completion_rules.quality_and_attention
        model.interview.set_completion_rule(rule)
        #
        remaining = range(level.last, len(level))
        #
        a_budget = model.interview.attention.budget
        a_current = model.interview.attention.current
        a_allowance = a_budget - a_current
        a_allowance = max(0, a_allowance)
        #allowance must be greater than or equal to zero
        #
        total_need = 0
        for i in remaining:
            item = level[i]
            q_standard = item.guide.quality.standard
            q_current = item.guide.quality.current
            item_need = q_standard - q_current
            item_need = max(0, item_need)
            #positive need only
            total_need += item_need
        #
        rationing = False
        if total_need > available_attention:
            rationing = True
        #
        if not rationing:
            fp = self.selector_quality(level, model)
        else:
            attention_cap = available_attention / len(remaining)
            #
            for i in remaining:
                item = level[i]
                item.guide.attention.budget = attention_cap
                #
                if rule(item):
                    #work on item is complete
                    item.guide.complete = True
                    continue
                else:
                    #
                    item.guide.complete = False
                    fp = item
                    level.last = i
                    break
        #
        return fp

    def selector_attention_depth(self, level, model):
        #
        #run quality selection as usual, stop when run out of attention
        #
        fp = None
        #
        remaining = range(level.last, len(level))
        #
        a_budget = model.interview.attention.budget
        a_current = model.interview.attention.current
        a_available = a_budget - a_current
        a_available = max(0, a_allowance)
        #allowance must be greater than or equal to zero
        if a_available:
            fp = selector_quality(level, model)
        else:
            #no op if out of attention, keep fp blank
            pass
        #
        return fp
        #
    
    def set_progress(self, model):
        #blah
        pass

    def routine_basic(self, model):
        #most basic
        #treats all positive-priority items as same level of importance
        #not sensitive to attention 
        path = model.interview.path
        model.interview.levels = self.prioritize_single(path)
        fp = self.focus(model,
                        self.selector_quality)
        #
        return fp

    def routine_priority_tiers(self, model):
        #prioritizes items into different levels
        #picks out first open one
        #
        path = model.interview.path
        model.interview.levels = self.prioritize_multi(path)
        fp = self.focus(model,
                        self.selector_quality)
        #
        return fp
    
    def routine_attention_simple(self, model):
        #like p1, but stops working when there is no more attention available
        path = model.interview.path
        model.interview.levels = self.prioritize_multi(path)
        fp = self.focus(model,
                        self.selector_attention_depth)
        #
        return fp

    def routine_attention_budget(self, model):
        #tries to allocate attention ratably
        path = model.interview.path
        model.interview.levels = self.prioritize_multi(path)
        fp = self.focus(model,
                        self.selector_attention_breadth)
        #
        return fp

#
IC._protocol_routines = dict()
IC._protocol_routines[0] = IC.routine_basic
IC._protocol_routines[1] = IC.routine_priority_tiers
IC._protocol_routines[2] = IC.routine_attention_simple
IC._protocol_routines[3] = IC.routine_attention_budget


    
        


    
