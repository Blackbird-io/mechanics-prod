#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TimePeriod
"""

Module defines TimePeriod class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimePeriod            a snapshot of data over a period of time. 
====================  ==========================================================
"""





#imports
import copy
import datetime
import time
import BBExceptions
import BBGlobalVariables as Globals

from DataStructures.Platform.ID import ID
from DataStructures.Platform.Tags import Tags




#globals
#n/a

#classes
class TimePeriod(Tags):
    """

    TimePeriod objects represent periods of time and store a snapshot of some
    data during that period in their ``content`` attribute.

    Class represents an interval that includes its endpoints: [start, end].
    
    If one thinks of a TimeLine as a clothesrack, TimePeriods are individual
    hangers. This structure enables Blackbird to track the evolution of the data
    over real-world wall/calendar) time. 

    The data in ``content`` is usually a top-level business unit. TimePeriod
    provides a reference table ``bu_directory`` for objects that the data
    contains. The bu_directory tracks objects by their bbid. Only one object
    with a given bbid should exist within a TimePeriod. bbid collisions within
    a time period represent the time-traveller's paradox. 
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; all business units in this period, keyed by bbid
    content               pointer to content, usually a business unit
    end                   datetime.date; last date in period 
    id                    instance of ID class
    length                float; seconds between start and end
    prior                 pointer to immediately preceding time period
    start                 datetime.date; first date in period.
    ty_directory          dict; keys are strings, values are sets of bbids
    
    FUNCTIONS:
    __str__               basic print, shows starts, ends, and content
    class dyn_cal_manager  descriptor for length, start_date, end_date
    clear()               clears content, resets bu_directory
    copy()                returns new TimePeriod with a copy of content
    extrapolate_to()      updates inheritance then delegates to Tags
    ex_to_default()       creates result from seed, sets to target start/end
    ex_to_special()       starts w target copy, new content is seed.ex(target)
    resetDirectory()      sets bu_directory to blank dictionary
    selectBottomUnits()   returns a list of components w/o other biz units
    setContent()          sets instance content to argument
    setPrior()            sets pointer to preceding time period    
    ====================  ======================================================
    """
    def __init__(self, start_date, end_date, content = None):
        Tags.__init__(self)
        self.start = start_date
        self.end = end_date
        #
        self.bu_directory = {}
        self.ty_directory = {}
        #
        self.content = content
        self.id = ID()
        self.prior = None
        #
        #the current approach to indexing units within a period assumes that
        #Blackbird will rarely remove existing units from a model. both
        #the ``bu`` and ``ty`` directories are static: they do not know if
        #the unit whose bbid they reference is no longer in their domain. if
        #this poses a problem, can change them to properties.
        #
        #the potential for trouble is more significant for ty_directory. a unit
        #can theoretically change type.
        #
        #approach: type is a property. can set if blank, otherwise raises error.
            #to change, need to reset_type() and then set again.
            #error on del

    def __str__(self):
        dots = "*"*Globals.screen_width
        s = "\t starts:  \t%s\n" % self.start.isoformat()
        e = "\t ends:    \t%s\n" % self.end.isoformat()
        c = "\t content: \t%s\n" % self.content
        result = dots+"\n"+s+e+c+dots+"\n"
        return result 

    def clear(self):
        """


        TimePeriod.clear() -> None


        Method sets content to None and runs resetDirectory().
        """
        self.content = None
        self.resetDirectory()
        
    def copy(self, enforce_rules = True):
        """


        TimePeriod.copy(enforce_rules) -> TimePeriod


        Method returns a new TimePeriod object whose content is a class-specific
        copy of the caller content. 
        """
        result = Tags.copy(self,enforce_rules)
        result.start = copy.copy(self.start)
        result.end = copy.copy(self.end)
        if self.content:
            new_content = self.content.copy(enforce_rules)
            result.setContent(new_content, updateID = False)
        #same id namespace (old model)
        #
        return result
    
    def extrapolate_to(self,target):
        """


        TimePeriod.extrapolate_to(target) -> TimePeriod


        Method returns a new time period with a mix of seed and target data.

        Method updates tags on seed and target and then passes them to standard
        Tags.extrapolate_to() selection logic. 
        """
        self.inheritTags(recur = True)
        target.inheritTags(recur = True)
        result = Tags.extrapolate_to(self,target)
        return result
    
    def ex_to_default(self,target):
        """


        TimePeriod.ex_to_default(target) -> TimePeriod


        Method used for extrapolation when existing target content can be
        discarded. Method returns a new TimePeriod object that represents a
        projection of seed (caller) content into the point in time specified by
        target.

        NOTE: Method assumes that both seed and target have up-to-date inherited
        tags. It is up to user to deliver accordingly. 

        Method first creates a vanilla shallow copy of the caller, then runs
        a class-specific .copy on the vanilla alt_seed to create the result
        shell. Method sets the time endpoints on the result to those specified
        by target and creates a copy of seed content. Method concludes by
        running setContent(new_content) on the result. The last step spread the
        period and date information down the content structure and updates the
        result's bu_directory with the bbid's of all BusinessUnits it contains.
        
        NOTE2: For best results, may want to clear and re-inherit tags on result
        after method returns it. 
        """
        #
        #step 1: make container
        seed = self
        alt_seed = copy.copy(seed)
        #keep all attributes identical, but now can zero out the complicated
        #stuff
        alt_seed.clear()
        result = alt_seed.copy(enforce_rules = True)
        #use class-specific copy to create independent objects for any important
        #container-level data structures; Tags.copy() only creates new tag lists 
        result = Tags.ex_to_special(result,target,mode = "at")
        #updates result with those target tags it doesnt have already. "at" mode
        #picks up all tags from target. other attributes stay identical because
        #Tags uses a shallow copy.
        #
        #step 2: configure and fill container
        result.start = copy.copy(target.start)
        result.end = copy.copy(target.end)
        if seed.content:
            new_content = seed.content.copy(enforce_rules = True)
            result.setContent(new_content, updateID = False)
        result.setPrior(seed)
        #
        #return container
        return result        
        
    def ex_to_special(self,target):
        """


        TimePeriod.ex_to_special(target) -> TimePeriod


        Method used for extrapolation when seed content must pick up special
        attributes from target. 

        NOTE: Method assumes that both seed and target have up-to-date inherited
        tags. It is up to user to deliver accordingly.

        Method creates a shell from seed, has that shell inherit target tags and
        time points. Method then sets the result content to a new object
        extrapolated from seed to target.

        NOTE2: For best results, may want to clear and re-inherit tags on result
        after method returns it. 
        """
        #
        #step 1: make container
        seed = self
        alt_seed = copy.copy(seed)
        #alt_target and target have identical attributes (alt_a is t_a)
        alt_seed.clear()
        #leave out the complicated stuff
        result = alt_seed.copy(enforce_rules = True)
        #use class-specific copy to create independent objects for any important
        #container-level data structures; Tags.copy() only creates new tag lists 
        #
        #supress rule enforcement because result and target are conceptually the
        #same object.
        result = Tags.ex_to_special(target,result,mode = "at")
        #updates result with those target tags it doesnt have already. "at" mode
        #picks up all tags from target. other attributes stay identical because
        #Tags uses a shallow copy.
        #
        #configure and fill container
        result.start = copy.copy(target.start)
        result.end = copy.copy(target.end)
        bu_seed = seed.content 
        bu_target = target.content
        bu_new = bu_seed.extrapolate_to(bu_target)
        result.setContent(bu_new, updateID = False)
        result.setPrior(seed)
        #
        #return container
        return result

    def resetDirectory(self):
        """


        TimePeriod.resetDirectory() -> None


        Method sets instance.bu_directory and instance.ty_directory to blank
        dictionaries. 
        """
        self.bu_directory = {}
        self.ty_directory = {}

    def selectBottomUnits(self):
        """


        TimePeriod.selectBottomUnits() -> list


        **OBSOLETE**

        Legacy interface. Delegates all work to select_bottom_units().

        During delegration, method permits runs on empty pool to ensure
        that new results stay consistent with old ones for calls on instances
        with no registered units in the directory. 
        """
        result = self.select_bottom_units(run_on_empty = True)
        return result
    
    def select_bottom_units(self, pool = None, run_on_empty = False):
        """


        TimePeriod.select_bottom_units([pool = None
          [, run_on_empty = False]]) -> list


        Method returns a list of units in pool that have no components. If
        ``pool`` is None, method will build its own pool from all keys in
        the instance's bu_directory.

        Method will raise error if asked to run on an empty pool unless
        ``run_on_empty`` == True.
        
        NOTE: method performs identity check (``is``) for building own pool;
        accordingly, running a.select_bottom_units(pool = set()) will raise
        an exception.         
        """
        if pool is None:
            pool = sorted(self.bu_directory.keys())
        if any([pool, run_on_empty]):
            #
            foundation = []
            #
            for bbid in pool:
                bu = self.bu_directory[bbid]
                if bu.components:
                    continue
                else:
                    foundation.append(bu)
            #
            return foundation
            #
        else:
            c = "method will not run on empty pool unless explicitly instructed to do so"
            raise ErrorOfSomeSort(c) 
            
                            
    
    def setContent(self,bu,updateID = True):
        """


        TimePeriod.setContent(bu) -> None


        Method connects the bu to the instance and sets the bu as instance
        content.

        NOTE: ``updateID`` should only be True when adding external content to
        a model for the first time (as opposed to moving content from period to
        period or level to level within a model).

        TimePeriods in a Model all share the model's namespace_id. Accordingly,
        a BusinessUnit will have the same bbid in all time periods. The
        BusinessUnit can elect to get a different bbid if it's name changes, but
        in such an event, the Model will treat it as a new unit altogether.
        """
        bu.fitToPeriod(self, recur = True, updateID = updateID)
        #must fit bu to period before proceeding with analysis in case the bu
        #is a raw shell that has never been assigned a bbid (ie at model start)
        #bu.fitToPEriod(updateID= True) assigns the bu a valid bbid within the
        #model namespace. this method can then proceed instead of rejecting
        #perfectly reasonable content.
        if bu.id.bbid:
            self.resetDirectory()
            bu.updateDirectory(recur = True, overwrite = False)
            #.updateDirectory() will raise an exception if it detects uuid
            #collisions among any components.
            self.content = bu
        else:
            c = "Cannot add content without a valid bbid."
            raise BBExceptions.IDError(c)
    
    def setPrior(self,prior_period):
        """


        TimePeriod.setPrior(prior_period) -> None


        Method sets instance.prior to argument. 
        """
        self.prior = prior_period


      
