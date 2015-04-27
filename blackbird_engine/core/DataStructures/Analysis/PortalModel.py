#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.PortalModel
"""

Module defines class that follows the Engine-Wrapper API PortalModel schema
and converts rich objects into schema-compliant dictionaries.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
PortalModel        object that follows Engine-Wrapper API schema
====================  ==========================================================
"""




#imports
import copy
import dill

from .ReadyForPortal import ReadyForPortal




#globals
#n/a

#classes
class PortalModel(ReadyForPortal):
    """

    Class defines an object that translates a question the Engine wishes to ask
    the user into the Engine API's PortalQuestion schema.

    Use to_portal() to generate clean dictionaries suitable for external
    delivery.

    PortalQuestion objects do not rely on any QuestionManager functionality. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    array_caption         string that appears above arrays of input_elements
    comment               explanation string that appears below the prompt
    input_array           list of InputElement objects
    input_type            string, controls widgets displayed in browser
    input_sub_type        string, provides additional context for Portal
    prompt                main question
    progress              float; completion indicator for interview, 0< p <=1
    short                 string; 2-3 question summary for tracker panel
    topic_name            string; appears in user-facing browser outline
    transcribe            bool; whether portal should show question to lenders

    FUNCTIONS:
    to_portal()           returns attr : attr_val dictionary
    ====================  ======================================================
    """
    def __init__(self):
        pm_attrs = ["e_model",
                    "industry",
                    "summary",
                    "business_name",
                    "business_id",
                    "user_context",
                    "tags"]
        #
        ReadyForPortal.__init__(self, pm_attrs)
        #
        self.e_model = None
        self.industry = None
        self.summary = None
        self.business_name = None
        self.business_id = 99999999
        self.user_context = None
        self.tags = None

    def to_portal(self, seed = None):
        """


        PortalModel.to_portal(seed) -> dict()

        
        Method returns a dictionary object, keyed by attribute name for a
        standard, fresh instance of cls and carrying values from matching
        seed attributes.

        Method delegates work to ReadyForPortal.to_portal, then modifies the
        output by manually extracting the industry. 
        """
        prelim = ReadyForPortal.to_portal(self)
        #prelim is a dictionary;
        result = prelim.copy()
        if seed:
            if seed.portal_data:
                result.update(seed.portal_data)
            #
            seed.portal_data.clear()
            flattened = dill.dumps(seed)
            result["e_model"] = flattened
            #
            result["industry"] = seed.header.profile.get("industry")
            result["summary"] = seed.summary.copy()
        #summary.copy() will return a plain vanilla dictionary
        #
        del result["_var_attrs"]
        #
        return result
        
    

####-------------------------------------------------------------------------------------------------------
    #def to_summary(self, seed)
        #returns a BusinessSummary
        #currently returns None
        #or may be simple financials?
            #use a template that's also the keys for LayoutTable
            #rev
            #
        #expensive method, so shouldnt run all the time
        #should be on model?
            #so can summarize trends across stuff?
            #should probably be a topic of its own
            #but then only runs occasionally
            #ideally should run whenever model changes? 
            #should go on interview.summary
                #should probably separate conversion to PortalSummary from
                #creation of a summary model
            #Topic.summarize_model()
                #does complex stuff
                    #how? by passing the model to Analyzer on wrap_topic?
                    #no, by tagging topic.summarize_on_wrap
                    #then topic will automatically run summarize()
                    #or ask Analyzer to run summarize?
                        #kind of implies two focal points?
                        #might be more than one summarizer?
                        #if summarizer runs extrapolate, could take a minute or two
                #so what to do...
                    #option 1: only run summary when model is complete
                    #option 2: have portal get summary when shows summary page and for market
                    #option 3: suck it up and run summary whenever a topic requests it
                    #option 4: have topics request a new summary and then run it when portal calls?
                    #option 5: only run summary when analyzer delivers topic to caller
                #for now:
                    #summary topic will just copy stuff from financials for current period
                    #so that's easy
                    #but should label some fields as lenders or borrowers only
                #for future:
                    #extrapolate
                    #sum results across multiple periods
                    #summary should have all 
                #each path should have verification as a line item
                #
                
                        
                    #
                    #
                #puts result on M.interview.business_summary or M.summary, in form
                #of list of lineitems
            #PortalModel.to_portal()
                #set summary to BusinessSummary.to_portal()
                #which basically takes an internal schema (LayoutObject) and updates it
                #how does it do the update? 
                    #for every attribute of BusinessSummary
                    #
                    #
            #
            #
            #
            #for now, have
            #
            #add detailed financials to lender view ? for Day 1
            #
            #
            #
            #also need to put credit capacity on
            #check if model has analytics
            #then pull out max at first, multiply it by 80% [ from Globals.capacity_haircut]
            #
            #but that means needs to happen at IC level
            #or at Analyzer level, once it gets the end_interview result?
            #M.business_summary = summary
            #so this tilts in the direction of running the whole thing through Analyzer
            #especially since there may be multiple summary topics
            #
            #so, Analyzer, on end_interview does what?
                #calls process_analytics()
                    ##already built

                #calls summarize_model()
                    ##sets M.interview.focalPoint to a designated summary line?
                    ##Yenta picks out a topic
                    ##Topic generates a fresh BusinessSummary for Model.business_summary
                    ##BusinessSummary is a dictionary w line names to values
                    ##
                #
                #summarize_model() can always run a selection process on summary
                    #select_topic
                        #
                    #refine = if refine, could use a different object
                    #_path_end = [analyze_line, summarize_line]
                    #
                    #
                #price_model() can always run a selection process on valuation or smtg
            #
            #timeLine.extrapolate_all()
                #starting_period = x
                #extrapolater period_now to period_next

            #M.fill_timeline():
            #M.compute_across_time():
            #M.extrapolate_all():
                #segments = M.timeLine.get_date_segments()
                #future = segments[2]
                #past = segments[0]
                #future_period_1 = M.timeline[future[0]]
                #
                #past_period_1
                #M.currentPeriod.extrapolate_to
                    #now.extrapolate_to(future[0])
                    #for i in range(len(future)):
                        #now_date = future[i]
                        #next_date = future[i+1]
                        #now_period = self.timeLine[now_date]
                        #next_period = self.timeLine[next_date]
                        #now_period.extrapolate_to(next_period)
                #
                
                        #now.extrapolate_to(next)
                    
            
                #get past
                
                    #

            #timeLine.get_ordered()
            #timeLine.get_past()
            #timeLine.get_future():
            #   #
            #
            #
            #
            #
            #
            #
            #
    
    
