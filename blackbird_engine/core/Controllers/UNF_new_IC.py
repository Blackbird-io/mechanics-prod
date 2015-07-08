#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.interview_controller

"""

Module defines the InterviewController class. IC objects process mqr messages to
identify the item where Blackbird should focus its analysis at a givne point in
time (the interview focal point). To do so, IC objects organize containers by
priority. IC objects then select items within priority levels based on whether
or not those items need additional work. IC objects can use several different
criteria (``protocols``) for organizing and selecting the focal point. See the
class docstring for more info on the difference between protocols. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
InterviewController   selects focal point for Blackbird analysis
====================  ==========================================================
"""




#imports
import BBExceptions

from . import UNF_completion_rules as completion_rules

from .Controller import Controller
from .UNF_level import Level




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

    The process() method provides the main, integrated interface; it accepts and
    returns mqr messages.

    IC objects delegate substantive work to one of several built-in versions of
    the search-and-prioritization routine. See doc strings for the values in
    in _protocol_routines for more info.    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _protocol             int; local state for protocol selection; 1 is default
    _protocol_routines    dict; CLASS attr, protocol : routine
    protocol              int; P, get _protocol, set iff in routine keys

    FUNCTIONS:
    prioritize_single()
    prioritize_multi()
    process()             in MQR message, sets model focal point
    set_progress()        sets progress bar
    wrap_interview()      ????
    
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """
    #class vars    
    def __init__(self):
        Controller.__init__(self)
        self._protocol = 1

    @property
    def protocol(self):
        """


        **property**


        Property returns instance._protocol

        Property setter accepts values that are in the class _protocol_routines
        dictionary. Setter raises ManagedAttributeError otherwise.
        """
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if value in self._protocol_routines:
            self._protocol = value
        else:
            c = "Unknown protocol. Attribute accepts only known keys for "
            c += "protocol routines."
            raise BBExceptions.ManagedAttributeError(c)
    
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
        routine = None
        #
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
            new_mqr = self.wrap_interview() #<------------------------------------------------------------need to make this
        else:
            self.set_progress(model) #<-------------------------------------------------------------------need to make this
            new_mqr = self.wrap_to_point() #<-------------------------------------------------------------need to make this
        #
        return new_mqr

    def prioritize_single(self, container):
        """


        IC.prioritize_single(iterable) -> dict()


        Method expects iterable to contain objects with a valid guide attribute.

        Method organizes all non-zero-priority items in iterable into a single
        level object. Method keyes that level to the highest priority Blackbird
        permits.

        For example, if the global maximum priority is 5, this method will
        always deliver a dictionary where levels[5] contains a level with all
        active-priority items in iterable. 
        """
        levels = dict()
        single_level = Level()
        levels[Globals.priority_max] = single_level
        for item in container.items():
            if not item.guide.priority.current:
                #skip 0-priority items
                continue
            else:
                single_level.append(item)
        #
        return levels

    def prioritize_multi(self, container):
        """


        IC.prioritize_multi(iterable) -> dict()


        Method expects iterable to contain objects with a valid guide attribute.

        Method organizes items in iterable into levels that correspond to their
        priority. Method skips zero-priority items. Method then returns a
        dictionary (``levels``) that contains each of the levels, keyed by
        priority. 
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
        """


        IC.focus(model, selector) -> fp
        

        Method returns an object that should serve as the model's focal point.
        Method returns ``None`` when all objects are complete.

        Method expects ``selector`` to be a callable that accepts two arguments
        (level and model) and returns an object suitable for focus.
        
        Method expects model.interview.levels to contain a dictionary of
        priority level objects keyed by priority. Method walks through the
        levels from most to least important.

        When method locates a level that is not yet complete, method applies
        selector to that level. If selector returns a True object, method stops
        analysis. Otherwise, when selector returns None, method marks the level
        as complete and moves on to the next one.
        """
        fp = None
        levels = model.interview.levels
        priorities = sorted(levels.keys(), reverse = True)
        for priority in priorities:
            level = levels[priority]
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
        """


        IC.selector_quality(level, model) -> fp

        
        Method selects a focal point from level.
        Method returns ``None`` when all items in level are complete.

        Method sets the interview completion rule to ``quality_only``. 

        Method applies the completion rule to each object in level, starting at
        the level.last position. Method stops as soon as it finds an object that
        fails the rule. Method marks complete = True on all objects that pass. 
        """
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
        """


        IC.selector_attention_breadth(level, model) -> fp

        
        Method selects a focal point from level.
        Method returns ``None`` when all items in level are complete.

        Method sets the interview completion rule to ``quality_and_attention``. 

        Method imposes attention rationing if the total quality need for the
        level exceeds the remaining attention budget for the model. Method
        computes quality need as the difference between an object's quality
        standard and existing quality.

        In the event the method needs to ration attention 
        
        Method applies the completion rule to each object in level, starting at
        the level.last position. Method stops as soon as it finds an object that
        fails the rule. Method marks complete = True on all objects that pass.
        """
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
            fp = self.selector_quality(level, model) #<-----------------------skip fork, make rule do nothing on blank budget
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
IC = InterviewController
IC._protocol_routines = dict()
IC._protocol_routines[0] = IC.routine_basic
IC._protocol_routines[1] = IC.routine_priority_tiers
IC._protocol_routines[2] = IC.routine_attention_simple
IC._protocol_routines[3] = IC.routine_attention_budget


    
        


    
