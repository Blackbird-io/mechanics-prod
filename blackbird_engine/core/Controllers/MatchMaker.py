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


Yenta class methods
-------------------

=================  ==============================================
Method             Description
=================  ==============================================
simpleSelect()     returns an instance of the best-matched topic
findEligible()     returns a list of any eligible topic objects
pickBest()         returns a list of best-scoring topic objects
tieBreaker()       returns the winner of tie-breaking routine
=================  ==============================================
"""




#imports
import random

import BBGlobalVariables
import DataStructures.Platform as Platform
import Managers.TopicManager as TopicManager
import Managers.tag_manager
import Tools.Parsing



#globals
#NOTE: class variables set at bottom of the module

#classes
#
#UPGRADE-S: module currently uses a lot of dictionary[key] calls to retrieve
#topic objects based on lists of tdexes passed from method to method. This is
#done to ensure that if methods store state (ie a list of tdexes) on an object
#somewhere in the ecosystem, that object can be deepcopied and pickled. Neither
#of those ops work on objects that point to modules. Topics are modules.
#
#However, speed improvements can be made by passing separate lists of tdexes for
#state and topics for speed, as long as we don't ever store the latter on other
#objects. 
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
    allScores          dict of TDEX: (cScore,pScore,trump)
    honor_trump

    FUNCTION:
    findEligible()     returns a list of any eligible topic objects
    pickBest()         returns a list of best-scoring topic objects
    reset()
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
        self.honor_trump = True
    
    def reset(self):
        """


        Yenta.reset() -> None


        Method sets ``percentScores`` and ``allScores`` on instance to blank
        dictionaries. 
        """
        self.percentScores = {}
        self.allScores = {}
        
    def selectTopic(self,Model):
        """

        Yenta.selectTopic(Model) -> Topic

        Method returns the best topic for analyzing model in its current state.
        Delegates all selection and introspection to other methods.
        
        """
        self.reset()
        newTopic = self.simple_select(Model)
        return newTopic

    def simple_select(self, Model):
        """


        Yenta.simple_select(Model) -> Topic

        
        Method finds and returns the best topic in the active catalog for
        analyzing the model. Actual object returned is a clean instance of the
        topic.

        The focal point specified on model.interview acts as the key benchmark
        for selection. If no topics apply to the focal point, method returns
        None.

        Method expects to find an informative ``guide`` attribute on the focal
        point.
        
        Selection algorithm:

        (1) select topics eligible for processing focal point
        (2) if more than one eligible topic exists, refine results by
        running Yenta.pickBest()
        (3) if pickBest() yields a tie, run Yenta.tieBreaker()
        
        Method returns None if topicCatalog contains no eligible topics.
        """
        topic = None
        selection = None
        readyToGo = None
        fPt = Model.interview.focalPoint
        fPt.guide.selection.increment(1)
        knownEligibles = fPt.guide.selection.eligibleTopics
        if knownEligibles != []:
            eligibles = self.findEligible(fPt, knownEligibles)
            if eligibles == []:
                eligibles = self.findEligible(fPt)
            #to avoid duplicating work, first check if any topics that looked
            #eligible before continue to be eligible. if some do, pick from
            #them. if none do, go through whole catalog again. 
        else:
            eligibles = self.findEligible(fPt)
        #update records on focusLine
        fPt.guide.selection.setEligibles(eligibles)
        #eligibles is a list of bbids
        best = None
        #pick the best candidates
        if len(eligibles) == 0:
            pass
        elif len(eligibles) == 1:
            selection = eligibles[0]
        else:
            best = self.pickBest(fPt,eligibles) #<---------------------------------------------------------------------------------make sure this is ok on bbids
            if len(best) == 1:
                selection = best[0]
            else:
                selection = self.tieBreaker(fPt,best) #<---------------------------------------------------------------------------------make sure this is ok on bbids
        #selection is a bbid, so need to retrieve actual topic from topic
        #catalog 
        if selection:
            topic = self.TM.local_catalog.issue(selection)
            fPt.guide.selection.recordUsedTopic(topic)
        else:
            fPt.guide.selection.recordDryRun()
        return topic
    
    def findEligible(self, L, pool = None, stripNone=True):
        """


        Yenta.findEligible(L[,pool=None[,stripNone=True]]) -> list


        Method returns a list of bbids for topics that are eligible for use on
        the criterion object L. L must have an .allTags attribute and a
        configured .guide object.

        The ``pool`` argument takes a list of bbids to review. If none is
        specified, method will use the keys in the active topic catalog (ie
        review the whole catalog).

        To determine eligibility, method calls retrieves the topic corresponding
        to each bbid from the topic catalog. Method then checks whether the
        topic's tags include all of the criterion's requiredTags (other than
        partOf). The method skips topics that appear on L's guide.usedTopics
        list.
        
        If ``stripNone`` is true (default), method strips out None objects from
        the L's eligibility criterion.
        """
        eligibles = []
        criterion = set(L.requiredTags)-{L.partOf}
        if not pool:
            pool = self.TM.local_catalog.by_id.keys()
        if stripNone:
            criterion = criterion - {None}
        for bbid in pool:
            if bbid in L.guide.selection.usedTopics:
                continue
                #topic already used
            T = self.TM.local_catalog.issue(bbid)
            missedReqs = criterion - set(T.tags.allTags)
            if missedReqs == set():
                #all requirements satisfied, topic eligible
                eligibles.append(bbid)
            else:
                continue
        return eligibles

    def pickBest(self, L, candidates, stripNone=True):
        """


        Yenta.pickBest(L, candidates[, stripNone]) -> list


        Method returns a list of bbids for the highest scoring topics
        among the candidates.

        ``candidates`` must be a list of bbids.

        ``L`` must be an object with an .allTags attribute.

        Method scores the topic corresponding to each candidate bbid based on
        the number of tags the topic shares with L. Each shared tag is worth 1
        point. The candidate(s) with the highest score are deemed the best.

        Method counts matches to both optional and required tags to allow it to
        score both pre-screened and raw candidate pools. In a pre-screened pool,
        each of the eligible candidates carries all of L's requiredTags.
        Accordingly, including requiredTag matches in each candidate's score
        increases all such scores by the same number; rankings remain the same.

        If ``stripNone`` is True (default), method does not count matches
        against None fields.

        Method ignores duplicate tags. All tags are matched casefolded.
        """
        self.allScores = {}
        bestScore = 0
        bestCandidates = []
        criteria = Tools.Parsing.stripCase(L, attr="allTags")
        #ignore duplicates
        criteria = set(criteria)
        if stripNone:
            criteria = criteria - {None}
        for bbid in candidates:
            T = self.TM.local_catalog.issue(bbid)
            cFeatures = Tools.Parsing.stripCase(T.tags,attr="allTags")
            cMatch = set(cFeatures) & criteria
            cScore = len(cMatch)
            pScore = cScore/len(T.tags.allTags)
            self.allScores[bbid] = [cScore, pScore, False]
            if cScore >= bestScore:
                bestCandidates.append(bbid)
                bestScore = cScore
        #save for later date
        return bestCandidates

    def tieBreaker(self,L,candidates,sripNone = True):
        """


        Yenta.tieBreaker(L, candidates[, stripNone = True]) -> bbid

        Method returns the bbid of the most suitable topic. 

        ``candidates`` must be a list of bbids.

        ``L`` must be an object with an .allTags attribute.

        Tests:
        First, weed out any candidates that do not have a trump card.
        Second, score by percentage of tags on Topic matched
        
        ?Third, score by tags on Financials (ie not specific to L)
        ?Fourth, score by tags on parentBU
        ?Fifth, score by tags on model
        """
        winner = None
        trump = Managers.tag_manager.loaded_tagManager.catalog["trump"]
        tCandidates = []
        self.percentScores = {}
        bestPercent = 0
        bestPercentCandidates = []
        stillTied = []
        for bbid in tCandidates:
            T = self.TM.local_catalog.issue(bbid)
            if trump in T.tags.allTags:
                tCandidates.append(bbid)
            cPercentScore = self.allScores[bbid][1]
            #allScores items are [T,cScore,pScore,trump]
            #method assumes that all candidates already have a valid entry in
            #self.allScores because Y.tieBreaker() never builds a list of
            #candidates from scratch
            if cPercentScore > bestPercent:
                bestPercent = cPercentScore
                #if this score is the best to date (and there are no equals),
                #then can overwrite existing bestPercentCandidates with a single
                #item list
                bestPercentCandidates = [bbid]
            elif cPercentScore == bestPercent:
                #if this score equals the previous high score, both topics
                #should be in the bestPercentCandidates
                bestPercentCandidates.append(bbid)
        tStatus = len(tCandidates)
        if tStatus == 1:
            winner = tCandidates[0]
        elif tStatus == 0:
            #no candidates have trump status
            #select one from general pool based on P Score
            plainHighScore = 0
            for bbid in candidates:
                activePScore = self.allScores[bbid][1]
                if activePScore > plainHighScore:
                    winner = bbid
                elif activePScore == plainHighScore:
                    stillTied.append(bbid)
                else:
                    continue
        else:
            trumpHighScore = 0
            #more than one candidate w trump status
            #select the tCandidate w the highest pScore
            for tdex in tCandidates:
                activePScore = self.allScores[bbid][1]
                if activePScore > trumpHighScore:
                    winner = bbid
                elif activePScore == trumpHighScore:
                    stillTied.append(tdex)
                else:
                    continue
        if stillTied != []:
            #winner = random.choice(stillTied)
            #no random selections
            winner = stillTied[0]
        return winner
        #
        #NOTE: need to make sure same topic doesnt go twice unless tagged
        #``recursive``; duplicative review should be in this module
        #
    

#Connect Yenta class to TopicManager so Yenta can access catalog
TopicManager.populate()
Yenta.set_topic_manager(TopicManager)
