"""
I run Yenta.selectTopic() on a model

selectTopic should:
    look inside currentPeriod.content (by default)
    ?should control focus (auto,tight,broad)
    step through the lineItems in financials
    can tag "matched" for those it touched
    can tag "active"
    can tag "more?"
    for each lineitem, go through topic catalog
    #go through lineitems
    #first lineitem you find that says "active", start search
    search through topic catalog
    return whatever you find first

MM only gets called between topics
Starter picks out first topic

should probably make select topic simple
so it just selects topics, doesnt ask whether analysis is done
and then completion controller can tag things "active" or "complete"
completion controller would be part of interview controller
can check re annoyance budget

so this way yenta cycles on the same thing
interrupt comes from:
   completion controller
   topics?
yenta controlled purely w selecting the best partner at any given time

alternative:
yenta tries to tell the partner when to stop also

simplify and add lightness


"""




#imports
import BBGlobalVariables
import DataStructures.Platform as Platform
import Managers.TopicManager as TopicManager
import Managers.tag_manager
import Tools.Parsing




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

    Object that selects the best topic for a given focal point. Expects focal
    point to have a guide attribute. Runs selection based on tags present on the
    focal point.

    Most callers will interface with a Yenta object through the
    selectTopic() method, which returns an instance of the most appropriate
    topic.
    
    =================  ==============================================
    Attribute             Description
    =================  ==============================================
    DATA:
    scores          dict of TDEX: (cScore, pScore, trump)

    FUNCTION:
    disconnect()
    find_eligible()     returns a list of any eligible topic objects
    pickBest()         returns a list of best-scoring topic objects
    reset()
    set_topic_manager() CLASS
    simple_select()     returns an instance of the best-matched topic
    tieBreaker()       returns the winner of tie-breaking routine    
    =================  ==============================================
    """
    TM = None
    
    @classmethod
    def disconnect(cls):
        cls.TM = None
        
    @classmethod
    def set_topic_manager(cls,new_TM):
        cls.TM = new_TM
        
    def __init__(self):
        self.scores = dict()
    
    def reset(self):
        """


        Yenta.reset() -> None


        Method sets instance.scores to a blank dictionary. 
        """
        self.scores = {}

    def find_eligible(self, target, pool = None):
        """


        Yenta.find_eligible(target[, pool = None]) -> list


        Method returns a list of bbids for topics that are eligible for use on
        target. Method expects target to have an .allTags attribute and a
        properly configured .guide object.

        The ``pool`` argument takes a list of bbids to review. If none is
        specified, method will use the keys in the active topic catalog (ie
        review the whole catalog).

        To determine eligibility, method calls retrieves the topic corresponding
        to each bbid from the topic catalog. Method then checks whether the
        topic's tags include all of the target's requiredTags (other than
        partOf).

        Method strips out None objects from target's eligibility criterion.
        
        NOTE: Method skips topics that appear in target's guide.usedTopics list.        
        """
        eligibles = []
        criterion = set(target.requiredTags) - {target.partOf}
        criterion = criterion - {None}
        #
        if not pool:
            pool = self.TM.local_catalog.by_id.keys()
        #
        pool = set(pool) - set(target.guide.selection.used)
        pool = sorted(pool)
        #sort pool into list to maintain stable evaluation order and results
        #
        for bbid in pool:
            topic = self.TM.local_catalog.issue(bbid)
            missed_reqs = criterion - set(topic.tags.allTags)
            if missed_reqs == set():
                #all requirements satisfied, topic eligible
                eligibles.append(bbid)
            else:
                continue
        #
        return eligibles

    def pick_best(self, target, model, candidates, combined = True):
        """


        Yenta.pick_best(target, model, candidates[, combined = True]) -> list


        Method returns a list of bbids for topics that scored highest against
        target.

        ``target`` must have an .allTags attribute.
        ``candidates`` must be a list of bbids.

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
        have the same raw score. 

        Method can score candidates in both pre-screened and raw pools. In a
        pre-screened pool, each candidates carries all target requiredTags.
        Target's required tags therefore increase each candidate's match score
        by the same integer. Candidate rankings in an **all-eligible** pool
        will therefore remain stable between counts that include required tags
        and those that do not. 

        If ``combined`` is True, method adds tags from target's senior objects
        to the scoring criteria. Method uses the following senior objects:
        
        -- the model
        -- target.parent (usually a more general line item or an instance of
           Financials)
        -- target.parent.parent (usually a more general line item, an instance
           of financials, or the business unit container for the target).

        Method excludes None from target criteria.
        """
        self.scores = dict()
        best_raw_score = 0
        best_candidates = []
        criteria = set(target.allTags)
        #use sets to ignore duplicate tags
        #
        if combined:
            #
            #supplement target tags with tags that appear on more ``senior``
            #objects in the model architecture.
            #
            parent = getattr(target, "parentObject", None)
            #target's parent will usually be a line or financials object
            tags_up_one = getattr(parent, "allTags", [])
            grandpa = getattr(parent, "parentObject", None)
            #target's grandpa will usually be a line, fins object, or business
            #unit
            tags_up_two = getattr(grandpa, "allTags", [])
            #
            criteria = criteria | set(tags_up_one) | set(tags_up_two)
            criteria = criteria | set(model.allTags)
            #
            #could use isinstance() to always select fins and bu, but that's
            #unpythonic. if that selection pattern turns out to be necessary,
            #should rethink parentObject attributes generally.
            #
        #
        criteria = criteria - {None}
        for bbid in candidates:
            topic = self.TM.local_catalog.issue(bbid)
            match = set(topic.tags.allTags) & criteria
            raw_score = len(match)
            rel_score = raw_score/len(topic.tags.allTags)
            #
            self.scores[bbid] = [raw_score, rel_score]
            #
            #save state on Yenta instance so subsequent routines can access
            #the information.
            #
            if raw_score >= best_raw_score:
                best_candidates.append(bbid)
                best_raw_score = raw_score
        #
        return best_candidates

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

        Method computes best fit against other candidates in a pool. If the
        focal point carries a cache of known topic ids, method computes
        rankings against that pool. Otherwise, or if no suitable topic exists
        in the pool, method computes rankings for all topics in the catalog.

        NOTE: The best candidate from an existing cache may be **worse** than
        a candidate located elsewhere in the catalog.

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
        chosen_bbid = None
        chosen_topic = None
        #
        fp = model.interview.focalPoint
        fp.guide.selection.increment(1)
        #
        known_eligibles = fp.guide.selection.eligible
        if known_eligibles != []:
            eligibles = self.find_eligible(fp, pool = known_eligibles)
            if eligibles == []:
                eligibles = self.find_eligible(fp)
            #
            #to avoid duplicating work, first check if any topics that looked
            #eligible before continue to be eligible. if some do, pick from
            #them. if none do, go through whole catalog again.
            #
        else:
            eligibles = self.find_eligible(fp)
        fp.guide.selection.set_eligible(eligibles)
        best = None
        #
        if len(eligibles) == 0:
            pass
            #method will check for dry runs before concluding
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
