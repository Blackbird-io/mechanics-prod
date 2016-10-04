# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.flow.yenta

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




# Imports
import topic_manager as TopicManager

from tools.for_tag_operations import build_basic_profile, build_combo_profile




# Constants
# n/a

#NOTE: class variables set at bottom of the module

# Classes

# UPGRADE-S: module currently uses a lot of dictionary[key] calls to retrieve
# topic objects based on lists of tdexes passed from method to method. Module
# uses this approach to ensure that pickle and deepcopy remain compatible with
# any selection state saved on the target object. Both deepcopy and pickle
# break on objects that point to modules. Topics used to be modules.

# Module can improve selection speed substantially by passing lists of actual
# topic objects from one sub-routine to another. Module would still have to save
# state via bbid only, since a topic can change tags between Matchmaker calls.

class Yenta():
    """

    The Yenta class selects the best topic to analyze an object. When deployed,
    Yenta evaluates the focal point of the stage at a given point in time.

    Yenta evaluates fit based on target and candidate tags. See individual
    methods for fit scoring algorithms.

    Yenta sees only those topics found in its TopicManager's local_catalog.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    scores                dict; topic id k, [raw_score, rel_score] value
    TM                    CLASS; pointer to TopicManager w populated catalog
    work                  instance storage for selection work; used for trace

    FUNCTION:
    check_topic_name()    check if topic matches target
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
    # for monitoring topic selection between questions
    diary = []

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
        self.work = None

    def check_topic_name(self, target, model, topic_name, combined = True):
        """


        Yenta.check_topic_name(target, model, topic_name
          [, combined = True]) -> (result, work)


        Method returns a bool result and a dictionary tracing the selection
        process. Method finds partial matches.

        """

        result = False
        # allow search by partial name
        try:
            topic_bbid = self.TM.local_catalog.by_name[topic_name]
        except KeyError:
            for known_key in sorted(self.TM.local_catalog.by_name):
                # sort to always
                match = known_key.find(topic_name)
                if match == -1:
                    continue
                else:
                    topic_bbid = self.TM.local_catalog.by_name[known_key]
                    break
            else:
                c = "No topic matches specified name."
                raise KeyError(c)

        pool_of_one = {topic_bbid}
        eligibles = self.find_eligible(target, model, pool_of_one,
                                       combined=combined, trace=True)

        if topic_bbid in eligibles:
            result = True
        work = self.trace
        missing_on_topic = work["scoring"][topic_bbid]["missing on topic"]
        missing_on_target = work["scoring"][topic_bbid]["missing on target"]

        line_1 = '\n\nTopic:    "%s"\n' % topic_name
        line_2 = 'Target:   %s\n' % target
        line_3 = "Eligible: %s\n\n" % str(result).upper()
        topic_header = "\nA. Tags missing from topic:\n"
        target_header = "\nB. Tags missing from target:\n"
        target_header += "(only exist when the topic specifies required tags)"

        print(line_1)
        print(line_2)
        print(line_3)

        # print details only if result is false
        if not result:
            print(topic_header)
            for (n, tag) in enumerate(sorted(missing_on_topic)):
                line = "\t%s. %s\n" % (n, tag)
                print(line)

        if not result:
            print(target_header)
            for (n, tag) in enumerate(sorted(missing_on_target)):
                line = "\t%s. %s\n" % (n, tag)
                print(line)
            print("\n")

        return result, work

    def find_eligible(self, target, model, pool=None, combined=True,
                      trace=False):
        """


        Yenta.find_eligible(target, model [, pool = None
          [, combined = True[, trace = False]]]) -> list


        Method returns a list of bbids for topics that are eligible for use on
        target. Method expects target to have an .tags.all attribute and a
        properly configured .guide object.

        The ``pool`` argument takes a list of bbids to review. If pool is None,
        method will use a sorted set of keys to the active topic catalog
        instead. That is, without a specific pool, method will review all topics
        in catalog for eligibility.

        To determine eligibility, method retrieves the topic that corresponds to
        to each bbid in pool from the topic catalog. Method then checks:

        (1) whether the topic's tags include each of the tags required by target
           (excluding target.relationships.parent.name); and
        (2) whether the **target's** tags include each of the tags required by
            topic, if any.

        Eligible topics are those that satisfy both conditions. If ``combined``
        is True, method evaluates condition (2) with respect to target's
        combined profile. In other words, if ``combined`` is True, method will
        check whether a given topic fits the whole model.

        NOTE: Method skips topics whose bbids appear in model's used set.

        If ``trace`` is True, method saves work (criteria and missing pieces for
        each topic) to instance.trace.
        """
        eligibles = []

        targ_criterion = target.tags.required | {target.name}
        targ_criterion = set(c.casefold() for c in targ_criterion if c)

        # UPGRADE-F: Can make selection process more open-ended by also removing
        # the target name from criterion. As is, naming binding creates a sort of
        # short cut for matches. Using only descriptive tags would shift
        # selection to a more functional match.

        if combined:
            targ_profile = build_combo_profile(target, model)
        else:
            targ_profile = build_basic_profile(target)
        #
        if not pool:
            pool = self.TM.local_catalog.by_id.keys()
        pool = sorted(pool)
        # sort pool into list to maintain stable evaluation order and results

        work = dict()
        work["target criterion"] = targ_criterion.copy()
        work["target profile"] = targ_profile.copy()
        work["eligibles"] = dict()
        if trace:
            work["revised pool"] = pool.copy()
            work["scoring"] = dict()

        for bbid in pool:
            topic_tags = self.TM.local_catalog.get_tags(bbid)
            topic_criterion = topic_tags.required - {None}
            topic_profile = topic_tags.all | {topic_tags.name}

            missing_on_topic = targ_criterion - topic_profile
            missing_on_target = topic_criterion - targ_profile
            prohibited_on_topic = topic_profile & target.tags.prohibited
            prohibited_on_target = targ_profile & topic_tags.prohibited
            used = bbid in model.target.used

            if trace:
                work["scoring"][bbid] = dict()
                work["scoring"][bbid]["topic profile"] = topic_profile
                work["scoring"][bbid]["topic criterion"] = topic_criterion
                work["scoring"][bbid]["missing on topic"] = missing_on_topic
                work["scoring"][bbid]["missing on target"] = missing_on_target

            if any((
                missing_on_topic,
                missing_on_target,
                prohibited_on_topic,
                prohibited_on_target,
                used,
            )):
                continue
            else:
                # all requirements satisfied, topic eligible
                eligibles.append(bbid)
                work["eligibles"][bbid] = {
                    'topic criterion': topic_criterion,
                    'topic profile': topic_profile,
                }

        self.trace = work
        self.diary.append(work)
        return eligibles

    def pick_best(self, target, model, candidates, combined=True):
        """


        Yenta.pick_best(target, model, candidates[, combined = True]) -> list


        Method returns a list of bbids for topics that scored highest against
        target.

        ``target`` must have an .tags.all attribute.
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

        self.scores = dict()
        best_candidates = []

        if combined:
            criteria = build_combo_profile(target, model)
        else:
            criteria = build_basic_profile(target)

        best_raw_score = 0
        for bbid in candidates:

            topic = self.TM.local_catalog.issue(bbid)

            match = criteria & build_basic_profile(topic)
            raw_score = len(match)
            rel_score = raw_score/len(topic.tags.all)

            self.scores[bbid] = [raw_score, rel_score]
            # save state on Yenta instance so subsequent routines can access
            # the information.

            if raw_score >= best_raw_score:
                best_raw_score = raw_score

            self.trace['eligibles'][bbid].update(
                topic=topic,
                raw_score=raw_score,
                rel_score=rel_score,
            )

        for (
            scored_bbid, [known_raw_score, known_rel_score]
        ) in self.scores.items():
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
        stage focal point better than any other candidates.

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

        fp = model.target.stage.focal_point
        fp.guide.selection.increment(1)

        eligibles = self.find_eligible(fp, model)

        if len(eligibles) == 0:
            pass
            # method will record dry run before concluding
        elif len(eligibles) == 1:
            chosen_bbid = eligibles[0]
        else:
            best = self.pick_best(fp, model, eligibles, combined=True)
            if len(best) == 1:
                chosen_bbid = best[0]
            else:
                chosen_bbid = self.tie_breaker(best)

        # check for dry runs and retrieve a copy of the topic w the chosen bbid
        if chosen_bbid:
            chosen_topic = self.TM.local_catalog.issue(chosen_bbid)
            fp.guide.selection.record_used_topic(chosen_topic)
        else:
            fp.guide.selection.record_dry_run()

        self.trace["chosen topic"] = chosen_topic
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

        return winner

# Connect Yenta class to TopicManager so Yenta can access catalog
TopicManager.populate()
Yenta.set_topic_manager(TopicManager)
