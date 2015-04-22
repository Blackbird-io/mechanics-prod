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
    data during that period in their ``content`` attribute. If one thinks of a
    TimeLine as a clothesrack, TimePeriods are individual hangers. This
    structure enables Blackbird to track the evolution of the data over
    (real-world wall/calendar) time. 

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
    end                   float; ending POSIX timestamp (secs since Epoch)
    end_date              datetime.date object corresponding to end timestamp
    id                    instance of ID class
    length                float; seconds between start and end
    prior                 pointer to immediately preceding time period
    start                 float; starting POSIX timestamp (secs since Epoch)
    start_date            datetime.date object corresponding to start timestamp
    
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
    def __init__(self, start_time, end_time, periodContent = None):
        Tags.__init__(self)
        self.start = start_time
        self.end = end_time
        self.bu_directory = {}
        self.content = periodContent
        self.id = ID()
        self.prior = None

    def __str__(self):
        dots = "*"*Globals.defaultScreenWidth
        s = "\t starts:  \t%s\n" % self.start_date
        e = "\t ends:    \t%s\n" % self.end_date
        c = "\t content: \t%s\n" % self.content
        result = dots+"\n"+s+e+c+dots+"\n"
        return result 
      
    class dyn_cal_manager:
        """

        Descriptor for ``start_date``, ``end_date``, and ``length``. Length is
        always the difference between period.end and period.start. Descriptor
        uses datetime.date.fromtimestamp() to calculate fresh date values. 
        """
        def __init__(self, targetAttribute):
            self.target = targetAttribute
          
        def __get__(self,instance,owner):
            if self.target == "start_date":
                result = datetime.date.fromtimestamp(instance.start)
                return result
            elif self.target == "end_date":
                result = datetime.date.fromtimestamp(instance.end)
                return result
            elif self.target == "length":
                result = instance.end - instance.start
                return result

        def __set__(self,instance,value):
            c = ""
            c += "``%s`` is a managed attribute. Direct writes prohibted."
            c = c % self.target
            raise BBExceptions.ManagedAttributeError(c)

    end_date = dyn_cal_manager("end_date")
    start_date = dyn_cal_manager("start_date")
    length = dyn_cal_manager("length")

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
        if self.content:
            new_content = self.content.copy(enforce_rules)
            result.setContent(new_content, updateID = False)
        #same id namesapce (old model)
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


        Method sets instance.bu_directory to a blank dictionary. 
        """
        self.bu_directory = {}

    def selectBottomUnits(self):
        """


        T.selectBottomUnits() -> list


        Method returns a list of ground-level components (components that do
        not contain any other business units).
        """
        foundation = []
        for bbid in sorted(self.bu_directory.keys()):
            bu = self.bu_directory[bbid]
            if bu.components == {}:
                foundation.append(bu)
            else:
                continue
        return foundation
    
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


      
