#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.Yenta

"""

This module defines the Yenta class. Yenta objects select the best topic to
analyze a given part of the model at a particular point in time. 
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Yenta                 selects best fitting topic to analyze an object
====================  ==========================================================
"""

#adding a line regarding blah

#imports
import Managers.TopicManager as TopicManager




#globals
#n/a
#NOTE: class variables set at bottom of the module

#classes
#
#UPGRADE-S: module currently uses a lot of dictionary[key] calls to retrieve
#topic objects based on lists of tdexes passed from method to method. Module
#uses this approach to ensure that pickle and deepcopy remain compatible with
#any selection state saved on the target object. Both deepcopy and pickle break
#on objects that point to modules. Topics used to be modules. 
#
#Module can improve selection speed substantially by passing lists of actual
#topic objects from one sub-routine to another. Module would still have to save
#state via bbid only, since a topic can change tags between Matchmaker calls.
#
class Yenta():
    """

    The Yenta class selects the best topic to analyze an object. When deployed,
    Yenta evaluates the focal point of the interview at a given point in time.

    Yenta evaluates fit based on target and candidate tags. See individual
    methods for fit scoring algorithms.

    Yenta sees only those topics found in its TopicManager's local_catalog.
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    scores                dict; topic id k, [raw_score, rel_score] value
    TM                    CLASS; pointer to TopicManager w populated catalog

    FUNCTION:
    build_basic_profile() return a set of target tags, used as simple criteria
    build_combo_profile() return a set of tags from target and model
    disconnect()          CLASS; set TM to None
    find_eligible()       return a list of 0+ ids for topics w all required tags
    pick_best()           return a list of 1+ ids for topics w most tags matched
    reset()               set scores to blank dictionary
    select_topic()        main interface, delegates all work
    set_topic_manager()   CLASS; set TM to point to the TopicManager
    simple_select()       returns topic that best matches focal point
    tie_breaker()         returns id w highest relative match score
    ====================  ======================================================
    """
    TM = None
    
    @classmethod
    def disconnect(cls):
        """


        Yenta.disconnect() -> None


        **CLASS METHOD**

        Method clears class TopicManager pointer (sets class.TM to None). 
        """
        cls.TM = None
        
    @classmethod
    def set_topic_manager(cls,new_TM):
        """


        Yenta.set_topic_manager(new_TM) -> None


        **CLASS METHOD**

        Method sets class TopicManager pointer to new_TM.
        """
        cls.TM = new_TM
        
    def __init__(self):
        self.scores = dict()


    def build_basic_profile(self, target):
        """


        Yenta.build_basic_profile(target) -> set()


        Method returns set of all tags on target, with None stripped out. 
        """
        try:
            criteria = set(target.allTags)
        except AttributeError:
            criteria = set(target.tags.allTags)
        criteria = criteria - {None}
        #
        return criteria
    
    def build_combo_profile(self, target, model):
        """


        Yenta.build_combo_criteria(target, model) -> set()


        Method returns the set of all tags found on target, target's parent,
        target's grandparent, and the model.

        When target is a LineItem, target's parent will usually be a line or a
        Financials object and its grandparent will usually be a line, Financials
        object, or a BusinessUnit. 
        """
        #
        parent = getattr(target, "parentObject", None)
        grandpa = getattr(parent, "parentObject", None)
        #
        tags_up_one = getattr(parent, "allTags", [])
        tags_up_two = getattr(grandpa, "allTags", [])
        #
        try:
            criteria = set(target.allTags)
        except AttributeError:
            criteria = set(target.tags.allTags)
        criteria = criteria | set(tags_up_one) | set(tags_up_two)
        criteria = criteria | set(model.allTags)
        criteria = criteria - {None}
        #
        return criteria    

    def build_target_requirements(self, target):
        reqs = set(target.requiredTags) - {None} - {target.partOf}
        #
        return reqs

    def build_topic_requirements(self, topic):
        #excludes name, returns set
        reqs = set(topic.tags.requiredTags[2:]) - {None}
        #
        return reqs
    
    def check_topic_name(self, target, model, topic_name, combined = True):
        #
        work = dict()
        result = False
        #
        topic_bbid = self.TM.local_catalog.by_name[topic_name]
        topic = self.TM.local_catalog.issue(topic_bbid)
        #
        targ_criterion = self.build_target_requirements(target)
        if combined:
            targ_profile = self.build_combo_profile(target, model)
        else:
            targ_profile = self.build_basic_profile(target)
        #
        topic_criterion = self.build_topic_requirements(topic)
        topic_profile = self.build_basic_profile(topic)
        #
        missed_target_reqs = targ_criterion - topic_profile
        missed_topic_reqs = topic_criterion - targ_profile
        #
        work["missed target reqs"] = missed_target_reqs
        work["missed topic reqs"] = missed_topic_reqs
        work["target criterion"] = targ_criterion
        work["target profile"] = targ_profile
        work["topic criterion"] = topic_criterion
        work["topic profile"] = topic_profile        
        #
        if any([missed_target_reqs, missed_topic_reqs]):
            result = False
        else:
            result = True
        #
        return (result, work)    
    
    def find_eligible(self, target, model, pool = None, combined = True):
        """


        Yenta.find_eligible(target, model
            [, pool = None[, combined = True]]) -> list


        Method returns a list of bbids for topics that are eligible for use on
        target. Method expects target to have an .allTags attribute and a
        properly configured .guide object.

        The ``pool`` argument takes a list of bbids to review. If pool is None,
        method will use a sorted set of keys to the active topic catalog
        instead. That is, without a specific pool, method will review all topics
        in catalog for eligibility. 

        To determine eligibility, method retrieves the topic that corresponds to
        to each bbid in pool from the topic catalog. Method then checks:

        (1) whether the topic's tags include each of the tags required by target
           (excluding target.partOf); and
        (2) whether the **target's** tags include each of the tags required by
            topic, if any.

        Eligible topics are those that satisfy both conditions. If ``combined``
        is True, method evaluates condition (2) with respect to target's
        combined profile. In other words, if ``combined`` is True, method will
        check whether a given topic fits the whole model.         
        
        NOTE: Method skips topics whose bbids appear in model's used set. 
        """
        eligibles = []
        targ_criterion = set(target.requiredTags) - {target.partOf}
        targ_criterion = targ_criterion - {None}
        #
        #UPGRADE-F: Can make selection process more open-ended by also removing
        #the target name from criterion. As is, naming binding creates a sort of
        #short cut for matches. Using only descriptive tags would shift
        #selection to a more functional match.
        #
        if combined:
            targ_profile = self.build_combo_profile(target, model)
        else:
            targ_profile = self.build_basic_profile(target)
        #
        if not pool:
            pool = self.TM.local_catalog.by_id.keys()
        #
        pool = set(pool) - model.interview.used
        pool = sorted(pool)
        #sort pool into list to maintain stable evaluation order and results
        #
        for bbid in pool:
            topic = self.TM.local_catalog.issue(bbid)
            topic_criterion = set(topic.tags.requiredTags[2:]) - {None}
            #
            missed_target_reqs = (targ_criterion -
                                  self.build_basic_profile(topic))
            missed_topic_reqs = topic_criterion - targ_profile
            if any([missed_target_reqs, missed_topic_reqs]):
                continue
            else:
                #all requirements satisfied, topic eligible
                eligibles.append(bbid)
        #
        return eligibles

    def pick_best(self, target, model, candidates, combined = True):
        """


        Yenta.pick_best(target, model, candidates[, combined = True]) -> list


        Method returns a list of bbids for topics that scored highest against
        target.

        ``target`` must have an .allTags attribute.
        ``candidates`` must be an iterable container of bbids.

        For each bbid, method pulls the topic from the catalog and counts how
        many target tags appear on the topic.

        Method ignores the disction between required and optional tags. Each
        matching tag increases the topic's raw_score by 1 point.

        Method also computes relative scores for each topic and stores them in
        **instance.scores**. Relative scores are the quotient of a topic's
        raw score and the total number of tags on that topic. Relative scores
        represent that quality of fit for a given topic, measured against
        that topic's best possible outcome. Yenta's tie_breaker() routine
        uses relative scores to select the best candidates when two or more 
        candidates have the same raw match score. 

        Method can score candidates in both pre-screened and raw pools. In a
        pre-screened pool, each candidates carries all target requiredTags.
        Target's required tags therefore increase each candidate's match score
        by the same integer. As a result, candidate rankings in an
        **all-eligible** pool will remain stable between counts that include
        required tags and those that do not. 

        If ``combined`` is True, method adds tags from target's senior objects
        to the scoring criteria. Method uses the following senior objects:
        
        -- the model
        -- target.parent (usually a more general line item or an instance of
           Financials)
        -- target.parent.parent (usually a more general line item, an instance
           of financials, or the business unit container for the target).

        Method excludes None from target criteria.
        """
        #
        #Algorithm:
        # - first, score all the candidates and set the highest raw score as
        #   the selection standard
        # - second, pick out any scored candidate that matches the standard
        #
        #Have to separate scoring from selection to make sure that every topic
        #has to live by the same standard. Otherwise, if bad topics go in front
        #of good ones in candidates, the standard will be low at the outset and
        #high later, so ``best_candidates`` will include sub-par topics.
        #
        self.scores = dict()
        best_candidates = []
        #
        if combined:
            criteria = self.build_combo_profile(target, model)
        else:
            criteria = self.build_basic_profile(target)
        #
        best_raw_score = 0
        for bbid in candidates:
            #
            topic = self.TM.local_catalog.issue(bbid)
            #
            match = criteria & self.build_basic_profile(topic)
            raw_score = len(match)
            rel_score = raw_score/len(topic.tags.allTags)
            #
            self.scores[bbid] = [raw_score, rel_score]
            #save state on Yenta instance so subsequent routines can access
            #the information.
            #
            if raw_score >= best_raw_score:
                best_raw_score = raw_score
        #
        for scored_bbid, [known_raw_score, known_rel_score] in self.scores.items():
            if known_raw_score >= best_raw_score:
                best_candidates.append(scored_bbid)
            else:
                continue
        return best_candidates

    def reset(self):
        """


        Yenta.reset() -> None


        Method sets instance.scores to a blank dictionary. 
        """
        self.scores = {}

    def select_topic(self, model):
        """


        Yenta.select_topic(model) -> Topic


        Method returns the topic that best matches the model's focal point.

        Method delegates selection logic to simple_select(). 
        """
        self.reset()
        new_topic = self.simple_select(model)
        return new_topic

    def simple_select(self, model):
        """


        Yenta.simple_select(model) -> Topic or None

        
        Method returns a clean instance of a topic that fits the current
        interview focal point better than any other candidates.

        Method computes best fit against all topics in the catalog.

        Method returns None if no topics in catalog are eligible to work on the
        model's focal point. 

        Method uses local best fit to make selection run faster. To select the
        best fit globally, clients can manually empty the cache on the focal
        point. Alternatively, clients can maintain focus on a particular object
        until Yenta records a dry run for that object. This second method is not
        strictly equivalent to the first, however, since earlier (cached)
        candidates could change the target at run-time in a way that alters
        selection criteria (e.g., by adding tags).
        
        Selection algorithm:

        (1) select all topics that contain each of target's required tags
        (2) rank the eligible topics by the total number of tags they match
        (3) break ties by selecting the topic with the highest relative match
        
        """
        best = None
        chosen_bbid = None
        chosen_topic = None
        #
        fp = model.interview.focal_point
        fp.guide.selection.increment(1)
        #
        eligibles = self.find_eligible(fp, model)
        #
        if len(eligibles) == 0:
            pass
            #method will record dry run before concluding
        elif len(eligibles) == 1:
            chosen_bbid = eligibles[0]
        else:
            best = self.pick_best(fp, model, eligibles, combined = True) 
            if len(best) == 1:
                chosen_bbid = best[0]
            else:
                chosen_bbid = self.tie_breaker(best)
        #
        #check for dry runs and retrieve a copy of the topic w the chosen bbid
        if chosen_bbid:
            chosen_topic = self.TM.local_catalog.issue(chosen_bbid)
            fp.guide.selection.record_used_topic(chosen_topic)
        else:
            fp.guide.selection.record_dry_run()
        #
        return chosen_topic
        
    def tie_breaker(self, candidates):
        """


        Yenta.tie_breaker(candidates) -> bbid


        Method returns the bbid of the candidate with the highest relative
        match score. Method uses Yenta.scores state to locate relative match
        scores for each candidate. Method expects ``candidates`` to be an
        iterable of bbids. 
        """
        winner = None
        top_rel_score = 0
        for bbid in candidates:
            rel_score = self.scores[bbid][1]
            if rel_score >= top_rel_score:
                winner = bbid
                top_rel_score = rel_score
            else:
                continue
        #
        return winner
        
#Connect Yenta class to TopicManager so Yenta can access catalog
TopicManager.populate()
Yenta.set_topic_manager(TopicManager)
