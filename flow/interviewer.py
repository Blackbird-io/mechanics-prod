#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: flow.interviewer

"""

Module defines the Interviewer class. Interviewer objects select a focal point
for further processing. Yenta and other objects then look to that focal point
as a criterion for selecting the next operation.

Interviewer selects a focal point from the path on the current model stage.
Interviewer can use one of several algorithms (``protocols``) to make the
selection. The protocols optimize for different qualities: speed, depth, etc.
See the class docstring for more info.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Interviewer           selects focal point for Blackbird analysis
====================  ==========================================================
"""




# Imports
import bb_exceptions

from data_structures.system.messenger import Messenger
from data_structures.guidance.guide import Guide

from tools import for_messages as message_tools

from . import completion_rules
from . import selection_rules

from .level import Level




# Constants
# n/a

##attention tracking: 
## - model has to keep fixed attention budget
##      - this can be a default number that then goes up or down with size or whatever
##
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


# Classes
class Interviewer:
    """

    Interviewer objects steer Blackbird interviews by selecting focal points
    for analysis and monitoring their completion.

    The process() method accepts and returns standard Blackbird mqr messages and
    acts as the main object interface. 

    Interviewer objects delegate substantive work to one of several built-in
    versions of the prioritization-and-search routine. The versions mix and match
    different subroutine elements. See their doc strings for more info.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _default_protocol     int; local state for protocol selection; 1 is default
    _protocol_routines    dict; CLASS attr, protocol : routine
    default_protocol      int; P, get _protocol, set iff in routine keys
    MR                    instance of Messenger class

    FUNCTIONS:
    focus()               pick highest priority focal point
    prioritize_multi()    return dict of items grouped into levels by priority
    prioritize_single()   reutnr dict of items in one, highest-priority level
    process()             in MQR message, sets model focal point
    r_basic()             complete every item in order 
    r_prioritized()       complete highest priority items first
    r_attentive_simple()  complete highest priority items until out of attn
    r_attentive_budget()  complete highest priority items with attn budget
    set_progress()        update progress to relative position of focal point
    wrap_interview()      return mqr msg with active question, end sentinel
    wrap_point()          return mqr msg with active question, active response
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """
    #class vars    
    def __init__(self):
        self.MR = Messenger()
        self._default_protocol = 1
        self._levels = dict()

    @property
    def default_protocol(self):
        """


        **property**


        Property returns instance._protocol

        Property setter accepts values that are in the class _protocol_routines
        dictionary. Setter raises ManagedAttributeError otherwise.
        """
        return self._default_protocol

    @default_protocol.setter
    def default_protocol(self, value):
        if value in self._protocol_routines:
            self._default_protocol = value
        else:
            c = "Unknown protocol. Attribute only accepts keys for known"
            c += "protocol routines."
            raise bb_exceptions.ManagedAttributeError(c)
    
    def focus(self, model, selector):
        """


        IC.focus(model, selector) -> fp
        

        Method returns an object that should serve as the model's focal point.
        Method returns ``None`` when all objects are complete.

        Method expects ``selector`` to be a callable that accepts two arguments
        (level and model) and returns an object suitable for focus.
        
        Method expects self._levels to contain a dictionary of priority
        level objects keyed by priority. Method walks through the levels from
        most to least important.

        When method locates a level that is not yet complete, method applies
        selector to that level. If selector returns a True object, method stops
        analysis. Otherwise, when selector returns None, method marks the level
        as complete and moves on to the next one.
        """
        fp = None
        priorities = sorted(self._levels.keys(), reverse = True)
        for priority in priorities:
            level = self._levels[priority]
            if level.guide.complete:
                continue
            else:
                fp = selector(level, model)
                if fp:
                    break
                else:
                    level.guide.complete = True
                    continue
        #
        return fp
        
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
        for item in container:
            if not item.guide.priority.current:
                #skip 0-priority items
                continue
            else:
                p = item.guide.priority.current
                peer_level = levels.setdefault(p, Level())
                peer_level.append(item)
        #
        return levels

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
        levels[Guide.HIGHEST_PERMITTED_PRIORITY] = single_level
        for item in container:
            if not item.guide.priority.current:
                #skip 0-priority items
                continue
            else:
                single_level.append(item)
        #
        return levels

    def process(self, message):
        """


        Interviewer.process(message) -> message


        Method identifies the object where Blackbird should focus its analysis
        given the current model state. Method tries to apply the protocol that
        the stage requests (stage.protocol_key). If the key is not in instance
        routines, method applies the instance's default protocol.

        Algorithm:

        (1) check whether model has a focal point already;
        (2) if a focal point exists, check if that point is complete;
        (3) if the focal point is complete or missing, use a routine to find
            a new focal point;
        (4) if the routine comes back empty, reset the interview cache and
            repeat step 3 to double-check;
        (5) if routine still can't find focal point, wrap the interview;
        (6) if a focal point exists, update progress; and
        (7) package results into message and deliver. 
        """
        #
        fp = None
        self.MR.prep(message)
        #
        model = self.MR.activeModel
        #
        #check known focal point
        old_fp = model.stage.focal_point
        known_rule = model.stage.completion_rule
        #
        protocol_key = model.stage.protocol_key
        routine = None
        #
        if known_rule:
            if known_rule(old_fp):
                pass
            else:
                fp = old_fp
                #rule says that old_fp is not yet complete. keep fp constant.
        if not fp:
            #
            #get here when model either: (1) doesn't have a focal point, (2)
            #doesnt have a known rule for testing the focal point, or (3) the 
            #known focal point satisfies the known rule and Blackbird needs to
            #find a new one.
            #
            if protocol_key not in self._protocol_routines:
                protocol_key = self.default_protocol
            routine = self._protocol_routines[protocol_key]
            #find and apply the protocol-specific processing routine. Interviewer
            #stores routines as class methods, so need to pass in the instance
            #explicitly.
            #
            fp = routine(self, model)
        if not fp:
            #double-check before concluding without a focal point
            model.stage.clear_cache()
            fp = routine(self, model)
            #if protocol routine doesnt find a focal point, reset cache and
            #try again. dont want to finish prematurely.
        #
        model.stage.set_focal_point(fp)
        #
        if not fp:
            new_mqr = self.wrap_interview(model)
        else:
            self.set_progress(model)   
            new_mqr = self.wrap_point(model)

        # set self._levels back to None to maintain statelessness
        # NEVER cache to self._levels in Interviewer, levels was once an
        # attribute of Outline (where levels could be cached), but is no more.
        self._levels = dict()

        return new_mqr
    
    def r_attention_budget(self, model):
        """


        IC.r_attention_budget(model) -> fp


        Method runs prioritize_multi() on model path. Method then applies focus
        using selector_quality_breadth.

        This routine tries to cover all necessary areas in a finite amount of
        time, at the expense of depth. 
        """
        #tries to allocate attention ratably
        path = model.stage.path
        self._levels = self.prioritize_multi(path)
        fp = self.focus(model, selection_rules.for_attentive_breadth)
        #
        return fp

    def r_attention_simple(self, model):
        """


        IC.r_attention_simple(model) -> fp


        Method runs prioritize_multi() on model path. Method then applies focus
        using selector_attention_depth.

        This routine stops the interview when it runs too long, but otherwise
        feels identical to r_prioritized(),
        """
        #like p1, but stops working when there is no more attention available
        path = model.stage.path
        self._levels = self.prioritize_multi(path)
        fp = self.focus(model, selection_rules.for_attentive_depth)
        #
        return fp

    def r_basic(self, model):
        """


        IC.r_basic(model) -> fp


        Method runs prioritize_single() on model path. Method then applies focus
        using selector_quality.

        Method treats all objects with defined priority as equally important. 
        """ 
        path = model.stage.path
        self._levels = self.prioritize_single(path)
        fp = self.focus(model, selection_rules.for_quality)
        #
        return fp

    def r_prioritized(self, model):
        """


        IC.r_prioritized(model) -> fp


        Method runs prioritize_multi() on model path. Method then applies focus
        using selector_quality.

        This routine provides intuitive analysis patterns for most models.
        """
        #prioritizes items into different levels
        #picks out first open one
        #
        path = model.stage.path
        ordered = path.get_full_ordered()
        self._levels = self.prioritize_multi(ordered)
        fp = self.focus(model, selection_rules.for_quality)
        #
        return fp
    
    def set_progress(self, model):
        """


        Interviewer.set_progress(model) -> None


        For stages that require progress tracking (stage.track_progress==True),
        method updates progress indicator.

        Method uses rough rule of thumb: progress is proportional to the
        position of the focal point in the interview path. This estimate works
        only for focal points that are actually in a model's path. Since other
        modules can set the focal point to any objects, including those that
        live outside a given model, method performs no-op when it cannot
        establish relative position.        
        """
        if model.stage.track_progress:
            fp = model.stage.focal_point
            path = model.stage.path
            if path:
                try:
                    steps = path.get_ordered()
                    i = steps.index(fp)
                    new_progress = i/len(steps)
                    new_progress = new_progress * 100
                    new_progress = round(new_progress)
                    model.stage.set_progress(new_progress)
                except ValueError:
                    #external focal point, do nothing            
                    pass

    def wrap_interview(self, model):
        """


        Interviewer.wrap_interview(model) -> mqr tuple


        Method marks current stage complete on model, returns a (M,Q,END)
        message.
        """
        stop = message_tools.END_INTERVIEW
        m = model
        q = self.MR.activeQuestion
        r = stop
        #
        model.stage.guide.complete = True
        print(model.stage)
        #
        self.MR.generateMessage(m, q, r)
        new_mqr = self.MR.messageOut
        #
        return new_mqr

    def wrap_point(self, model):
        """


        Interviewer.wrap_point(model) -> mqr tuple

        
        Method packages model, the current active question, and the current
        active response into an mqr message. Method then returns said message.
        Instance.MR stores the message until reset.
        """
        m = model
        q = self.MR.activeQuestion
        r = self.MR.activeResponse
        #
        self.MR.generateMessage(m, q, r)
        new_mqr = self.MR.messageOut
        #
        return new_mqr        
    
#
IC = Interviewer
IC._protocol_routines = dict()
IC._protocol_routines[0] = IC.r_basic
IC._protocol_routines[1] = IC.r_prioritized
IC._protocol_routines[2] = IC.r_attention_simple
IC._protocol_routines[3] = IC.r_attention_budget


    
        


    
