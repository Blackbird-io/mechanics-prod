#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: BusinessUnit
"""

Module defines BusinessUnit class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
templateFinancials    standard financials pattern

FUNCTIONS:
setDefaultFinancials() tracks ModelComponents interface. 

CLASSES:
BusinessUnit          structured snapshot of a business at a given point in time
====================  ==========================================================
"""




#imports
import copy
import datetime
import time
import BBExceptions
import BBGlobalVariables as Globals

from DataStructures.Guidance.Guide import Guide
from DataStructures.Platform.ID import ID
from DataStructures.Platform.Tags import Tags

from .Components import Components
from .Driver import Driver
from .DrContainer import DrContainer
from .Equalities import Equalities
from .Financials import Financials
from .Header import Header
from .LifeCycle import LifeCycle
from .Queue import Queue




#globals
#Tags class carries a pointer to the tag manager; access individual tags
#through that pointer
bookMarkTag = Tags.tagManager.catalog["bookmark"]
summaryTag = Tags.tagManager.catalog["summary"]
tConsolidated = Tags.tagManager.catalog["consolidated"]
tHardCoded = Tags.tagManager.catalog["hard"]

#classes   
class BusinessUnit(Tags,Equalities):
    """

    
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    analytics             instance of Analytics object, usually on top BUs
    components            instance of Components class, stores business units
    drivers               dict; tag/line name : set of driver bbids
    filled                bool; True if instance.fillOut() has run to completion
    financials            instance of Financials object
    guide                 instance of Guide object
    header                instance of Header object
    id                    instance of ID object
    life                  instance of LifeCycle object
    sig_consolidate       global signature updated for unit name
    tagSources            list; CLASS attribute, sources for tag inheritance
    
    FUNCTIONS:
    add_component()        adds bus with verified ids to components
    addComponent()        legacy interface for add_component()
    addDriver()           registers a driver under every name that appears in
                          its workConditions["name"] (including None)
    consolidate()         consolidates financials from every component
    consolidate_unit()    consolidates financials from one business unit
    derive()              uses drivers to determine values for financials
    fillOut()             integrates consolidate() and derive()
    fitToPeriod()         set refDate for bu and all components to period.end
    pretty_print()        show graphical summary of instance
    resetFinancials()     resets instance and (optionally) component financials
    setAnalytics()        attaches an object to instance.analytics
    setComponents()       attaches a Components object, sets partOf
    setDefaultFinancials()  CLASS, sets template financials
    setDrivers()          attaches a DrContainer object, sets partOf
    setFinancials()       attaches a Financials object from the right template
    updateDirectory()     enters all components into period's bu_directory
    verifyID()            checks that bbid is in period namespace
    ====================  ======================================================
    """

    irrelevantAttributes = ["allTags","filled","guide","id","parentObject",
                            "partOf"]
    tagSources = ["components","drivers","financials"]
        
    def __init__(self, name, fins = None):
        Tags.__init__(self,name) 
        self.analytics = None
        #
        self.components = None
        self.setComponents()
        #
        self.drivers = None
        self.setDrivers()
        self.filled = False
        #
        self.setFinancials(fins)
        #
        self.guide = Guide()
        self.header = Header()
        self.id = ID()
        #get the id functionality but do NOT assign a bbid yet
        self.life = LifeCycle()
        self.period = None
        gl_sig_con = Globals.signatures["BusinessUnit.consolidate"]
        self.sig_consolidate =  gl_sig_con % self.name
        
    def __hash__(self):
        return self.id.__hash__()

    def __str__(self, lines = None):
        """


        BusinessUnit.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls pretty_print() on instance. 
        """
        #
        #get string list from pretty_print, slap a new-line at the end of every
        #line and return a string with all the lines joined together.
        #
        if not lines:
            lines = self.pretty_print()
        #add empty strings for header and footer padding
        lines.insert(0, "")
        lines.append("")
        #
        box = "\n".join(lines)
        return box

    def add_component(self, bu, updateID = True):
        """


        BU.addComponent(bu[,updateID = True]) -> None


        Method prepares a bu and adds it to instance components.

        Method always sets bu namespace_id to instance's own namespace_id. If
        ``updateID`` is True, method then assigns a new bbid to the instance.

        Method raises IDNamespaceError if the bu's bbid falls outside the
        instance's namespace id. This is most likely if updateID is False and
        the bu retains an old bbid from a different namespace (e.g., when
        someone inserts a business unit from one model into another without
        updating the business unit's bbid).

        Method raises IDCollisionError if the period's directory already
        contains the new business unit's bbid.

        If all id verification steps go smoothly, method delegates insertion
        down to Components.addItem().       
        """
        bu.fitToPeriod(self.period, recur = True, updateID = updateID)
        if not updateID:
            if not bu.verifyID(recur = True):
                raise BBExceptions.IDNamespaceError
        #verifyID duplicative if method just reset all ids anyways
        bu.updateDirectory(recur = True, overwrite = False)
        self.components.addItem(bu)

    def addComponent(self, *kargs, **pargs):
        """

        Legacy interface, delegates all work to add_component
        
        """
        self.add_component(*kargs, **pargs)

    def addDriver(self,newDriver,*otherKeys):
        """


        BusinessUnit.addDriver(newDriver,*otherKeys) -> None


        Method registers a driver to names and tags of lines it supports.
        Method delegates all work to DrContainer.addItem().
        """
        self.drivers.addItem(newDriver,*otherKeys)
                  
    def clear(self):
        """


        BU.clear() -> None


        Method sets attributes in instance.tagSources to their default
        __init__ values.

        **NOTE: clear() will permanently delete data**
        
        """
        blank_bu = BusinessUnit(name = self.name)
        for attr in self.tagSources:
            blank_attr = getattr(blank_bu,attr)
            setattr(self,attr,blank_attr)

    def consolidate(self, *tagsToOmit, trace = False):
        """


        BU.consolidate(*tagsToOmit) -> None


        Method iterates through instance components in order and consolidates
        each living component into instance using BU.consolidate_unit()
        """
        if tagsToOmit == tuple():
            tagsToOmit = [bookMarkTag.casefold(), summaryTag]
        self.financials.buildDictionaries()
        ordered_components = self.components.getOrdered()
        for i in range(len(ordered_components)):
            component_on_deck = ordered_components[i]
            if not component_on_deck:
                continue
            else:
                self.consolidate_unit(component_on_deck,
                                      i,
                                      *tagsToOmit,
                                      refresh_dictionaries = False,
                                      trace = trace)
                #dont refresh dictionaries at beginning of consolidate unit;
                #main method already did so at the beginning, so they should
                #be fresh for component 1. after that, consolidate_unit will
                #refresh them when its routine inserts a new line into parent
                #financials.
        
    def consolidate_unit(self,
                         sub,
                         sub_position,
                         *tagsToOmit,
                         refresh_dictionaries = True,
                         trace = False):
        """


        BU.consolidate_unit()(sub,
                              sub_position,
                              [*tagsToOmit[,
                              [refresh_dictionaries = True[,
                              trace = False]]]) -> None
        

        -- ``sub`` should be a BusinessUnit object
        
        -- ``sub_position`` is sub's position in an ordered list of components;
           argument only matters for custom replica names
           
        -- ``tagsToOmit`` is a tuple of tags; method will ignore sub lines with
           any of these tags
           
        -- ``refresh_dictionaries`` is a bool value; if True, method will build
           dictionaries for instance financials from scratchbefore doing hard
           work, in case they are stale.

           This method will **always** build dictionaries after inserting a new
           line in instance financials to make sure that indeces are up to date.

           To maximize speed, caller should build dictionaries first, and then
           run this method with refresh_dictionaries == False. 
    
        -- ``trace`` is a bool value; if True, method prints comments during
           work.
        
        The Blackbird environment contemplates that BusinessUnits (``parents``)
        may contain multiple component BusinessUnits (``subs``). This method
        consolidates the financials of one sub into the caller instance
        (parent).

        The parent does NOT have to include sub in the parent's components for
        this method to run. 

        Method first fills out the sub, then integrates each line in sub's
        financials into parent financials. 



        The specific sub-to-parent integration algorithm has 5 stages:

        ************************************************************************
        STAGE 1: Check if the sub is alive.
        ************************************************************************

        Method performs no-op if sub is not alive. 

        ************************************************************************
        STAGE 2: Check if the sub LineItem is "informative".
        ************************************************************************
        For a living sub, method steps through each line in sub financials to
        check if the line is ``informative``. 

        ``Informative`` sub LineItems are those that provide insight into the
        meaningful structural or financial profile of the sub. Informative lines
        satisfy at least one of the following conditions:
        
            i)   the LineItem has a non-None name 
            ii)  the LineItem has a non-None value
            iii) the LineItem's allTags list is distinct from the default value
            ([None,None,<spacer>])
            
        Informative LineItems that satisfy condition (i) are ``named``
        LineItems. Informative LineItems that do not satisfy condition (i) but
        do satisfy condition (ii) or (iii) are ``unnamed.``

        NOTE: A lineitem that includes any tags specified in the method's
        ``tagsToOmit`` argument cannot be informative even if it otherwise
        satisifes one of the necessary conditions.

        By default, tagsToOmit include summaryTag and bookMarkTag. That is,
        bookmarks and summaries are per se uninformative and do not increment
        symmetric parent lineitems.         

        This method integrates some of the data from each informative sub line
        into parent's financials. Method skips uninformative sub lines. 

        ************************************************************************
        STAGE 3: Increment named LineItems that have symmetric names.
        ************************************************************************
        If a sub and parent LineItem have the same name, the value of sub
        increments the value of the parent.

        Specifically, for a given named sub lineitem, this method finds the
        **first** line in parent financials with the same name.
        
        Next, method increments the parent line by the sub line value, if the
        sub line has a specified (non-None value). Method skips sub lines with
        None values even if they are named.<-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------absorb tags?

        A signature from this method blocks drivers from modifying a line. 
        
        NOTE1: consolidate() **will** sign a parent line when a sub line
        specifies a value of 0, 0.00, decimal.Decimal(0), etc. 

        That is, setting a lineitem's value to 0 instead of None prevents
        drivers from modifying that lineitem. In the Blackbird environment, 0 is
        affirmative information. Only None signals the absence of information. 

        NOTE2: Only named sub LineItems are eligible for incrementation
        treatment, and only if their names are symmetric to a parent object.
        
        Named LineItems required a non-None value for LineItem.name. Therefore,
        a sub LineItem with .name == None will NOT increment a parent LineItem
        with a .name == None.

        ************************************************************************
        STAGE 4: Create & adjust replicas of name-asymettric sub LineItems.
        ************************************************************************

        For all informative LineItems that do not match the name of a parent
        line, this method copies the line into parent financials.

        Method attempts to insert these ``replica`` lines into parent in the
        same position relative to other lines as the sub line has in sub.

        Prior to insertion, method sets the name for any unnamed informative sub
        lines to a combination of (i) their sub_position and the first 3 tags on
        the sub line. As a result, unnnamed lines from one component should not
        increment the value of parent lines with identical tags.
        
        [UPGRADE-F: TAG-RICH EVO: may require sub lineitems to increment parent
        lineitems with matching or sub.superset tags]

        ************************************************************************
        STAGE 5: Insert replica LineItems into parent.financials.
        ************************************************************************

        Method places replica lines in parent financials to maintain relative
        position of the line against other items in sub financials. 

        Example:

        If lines are ordered [L1,L2,L3,L4] in sub financials, L1 should
        precede L2 in parent.financials. Other lines (LA, LB, LC) can go between
        L1 and L2 in parent because the position of L1 and L2 has no
        relationship to these other lines.

        By contrast, the following order of
        parent lines would violate the relative position of sub L3 and L4:
        
        [L1, ..., L2, ... L4,L3].
        
        Method uses Financials.spotGenerally() to locate the appropriate
        position for a replica. 
        """
        if tagsToOmit == tuple():
            tagsToOmit = [bookMarkTag.casefold(), summaryTag]
        tagsToOmit = set(tagsToOmit)
        parent = self
        if refresh_dictionaries:
            parent.financials.buildDictionaries()
        #stage 1: check that sub is alive
        if not sub.life.alive:
            pass
        else:
            sub.fillOut()
            for sLi in range(len(sub.financials)):
                #stage 2: check that lineItem is informative:
                subLine = sub.financials[sLi]
                sName = copy.copy(subLine.name)
                sValue = copy.copy(subLine.value)
                sPart = copy.copy(subLine.partOf)
                locPair = (subLine, sLi)
                #name, value, partOf all dynamic; for speed, get once to use
                #throughout the method
                #
                if not (sName or sValue):
                    continue
                if not tagsToOmit & set(subLine.allTags) == set():
                    continue
                if sName:
                    if sName in parent.financials.dNames.keys():
                        if not sValue:
                            continue
                            #no-op on blank-value name-symmetric lineitems
                            #leave open for drivers at parent
                        pLoc = max(parent.financials.dNames[sName])
                        parentLine = parent.financials[pLoc]
                        pValue = parentLine.value
                        if not pValue:
                            pValue = 0
                        newParentValue = pValue + sValue
                        subSuffix = " for Unit %s" % sub_position
                        sigWithUnit = parent.sig_consolidate + subSuffix
                        parentLine.setValue(newParentValue, sigWithUnit)
                        parentLine.inheritTagsFrom(subLine)
                        if trace:
                            print("incremented %s by %s" % (parentLine.name, sValue))
                        if tConsolidated not in parentLine.allTags:
                            parentLine.tag(tConsolidated)
                    else:
                        replica = subLine.replicate(compIndex = sub_position)
                        if sValue:
                            if tConsolidated not in replica.allTags:
                                replica.tag(tConsolidated)
                            #block derive for informative value lines; if value
                            #is at None, no tag, so derive can still write to
                            #line
                        subFins = sub.financials
                        L = parent.financials.spotGenerally(replica,subFins,sLi)
                        parent.financials.updatePart(replica)
                        parent.financials.insert(L,replica)
                        if trace:
                            print("replicated %s" % subLine.name)
                        parent.financials.buildDictionaries()
                else:
                    replica = subLine.replicate(compIndex = sub_position)
                    if tConsolidated not in replica.allTags:
                        replica.tag(tConsolidated)
                    #know that sValue must be true to get here, so tag
                    #consolidated and block derive
                    subFins = sub.financials
                    L = parent.financials.spotGenerally(replica,subFins,sLi)
                    parent.financials.updatePart(replica)
                    if trace:
                        print("replicated %s" % subLine)
                    parent.financials.insert(L,replica)
                    parent.financials.buildDictionaries()
                    #Upgrade-S: move UpdatePart into spotGenerally
        #
        #right now, consolidate() only allows incrementation for perfect
        #name symmetry: if unit1 has an unnamed informative lineitem with
        #tags x,y, &z, that informative lineitem will be replicated with a
        #constructed name. if unit2 then has an identically tagged unnamed
        #lineitem (also with x,y, & z tags), the unit2 lineitem will **not**
        #increment the lineitem created for unit1. the parent replica
        #lineitem for unit1 will be named "Unit1: X,Y,Z". that name will not
        #match the unnamed unit2 lineitem w identical tags. instead,
        #consolidate() will copy data from unit2 into a lineitem named
        #"Unit2: XYZ"
    
    def copy(self, enforce_rules = True):
        """


        BU.copy([enforce_rules = True]) -> BU


        Method returns a new business unit that is a deep-ish copy of the
        instance.

        The new bu starts out as a shallow Tags.copy() copy of the instance.
        The method then sets the following attributes on the new bu to either
        deep or class-specific copies of the instance values:

        - analytics
        - components
        - drivers
        - financials
        - header.profile
        - id (vanilla shallow copy)
        - life

        The class-specific copy methods for components, drivers, and financials
        all return deep copies of the object and its contents. See their
        respective class documenation for mode detail.
        """
        result = Tags.copy(self, enforce_rules)
        if self.analytics:
            alt_atx = copy.copy(self.analytics)
            alt_atx.parentObject = None
            alt_atx.disconnect()
            result.analytics = copy.deepcopy(alt_atx)
            #Upgrade-S: could also just set analytics on any copies to None
        r_comps = self.components.copy(enforce_rules)
        result.setComponents(r_comps)
        r_drivers = self.drivers.copy(enforce_rules)
        result.setDrivers(r_drivers)
        r_fins = self.financials.copy(enforce_rules)
        result.setFinancials(r_fins)
        result.guide = copy.deepcopy(self.guide)
        #have to make a deep copy of guide because it is composed of counter
        #objects. Guide shouldn't point to a business unit or model
        #
        result.header.profile = copy.deepcopy(self.header.profile)
        result.id = copy.copy(self.id)
        #header.profile should be the only object pointing to others on header
        result.life = self.life.copy()
        #
        return result

    def derive(self, *tagsToOmit):
        """


        BusinessUnit.derive([*tagsToOmit]) -> None


        Method for calculating the value of certain financials lineitems by
        using drivers. Method builds a Queue of applicable drivers for each
        LineItem in BusinessUnit.financials. Method then runs the drivers in the
        queue sequentially. Each LineItem gets a unique queue. Derive() ignores
        drivers that fail Queue.alignItems (misfits)

        In addition to any user-specified tags, method will not derive any lines
        carrying tags for consolidation or hard-coding.

        Method will try to use drivers specifically assigned to the line name in
        instance.drivers. If and only if the drivers dictionary for the line is
        empty, derive() will check if any unassigned (BU.drivers[None]) drivers
        match the line.
        
        NOTE: ALWAYS RUN BusinessUnit.consolidate() BEFORE BusinessUnit.Derive()
        """
        tagsToOmit = set(tagsToOmit)
        blockingTags = {tConsolidated,tHardCoded}
        tagsToOmit = tagsToOmit.union(blockingTags)
        #need to change tagging rules above to make sure BU.consolidate() tags
        #lines appropriately. also need to make sure that inheritTagsFrom() does----------------------------------------------------------
        #not pick up blockingTags
        for line in self.financials:
            if tagsToOmit & set(line.allTags) != set():
                continue
            line.clear()
            applicableDrivers = Queue()
            dKey = line.name
            if dKey in self.drivers.keys():
                dKey = dKey
            else:
                dKey = dKey.casefold()
            if dKey in self.drivers.keys():
                #drivers is a dictionary of tags to sets of bbids; to get actual
                #driver objects, have to call drivers.getDrivers()
                matching_drs = self.drivers.getDrivers(dKey)
                applicableDrivers.extend(matching_drs)
                applicableDrivers.alignItems()
            else:
                miscDrivers = self.drivers.getDrivers(None)
                for driver in miscDrivers:
                    if driver.canWorkOnThis(line):
                        if applicableDrivers.checkFit(driver):
                            applicableDrivers.append(driver)
                            applicableDrivers.alignItems()
            for driver in applicableDrivers:
                driver.workOnThis(line)
        
    def extrapolate_to(self,target):
        """


        BU.extrapolate_to(target) -> BU


        Returns a new business unit that combines seed and target
        attributes. Method delegates all work to Tags.extrapolate_to() selection
        logic.

        NOTE: BusinessUnit and several objects that form its attributes
        expressly delegate some or all of their extrapolation functionality to
        the Tags module.

        Therefore, these objects will **not** inherit any more
        specialized subclass methods. In the event future versions descend
        BusinessUnit or other objects from specialized subclasses of Tags, can
        fix by removing express delegation and relying on built-in Python MRO. 
        """
        result = Tags.extrapolate_to(self,target)
        return result
    
    def ex_to_special(self,target):
        """

       
        BU.ex_to_special(target) -> BU


        Method returns a new business unit that contains a blend of seed
        (caller) and target attributes.

        New unit starts as a copy of caller. Then, for each attribute in
        seed.tagSources, new unit inherits either (i) by default, a new object
        extrapolated from the seed and target attributes of the same name, or
        (ii) an unenforced copy of the target attribute, if that attribute does
        not permit modification. 
        """
        #
        #step 1: make container
        seed = self
        alt_seed = copy.copy(self)
        alt_seed.clear()
        #zero out the recursive attributes; a different part of the method works
        #on those
        result = alt_seed.copy(enforce_rules = True)
        #class-specific copy that picks up any class-specific data
        result = Tags.ex_to_special(result,target,mode = "at")
        #updates result with those target tags it doesnt have already. "at" mode
        #picks up all tags from target. other attributes stay identical because
        #Tags uses a shallow copy.
        #
        #step 2: fill container
        for attr in self.tagSources:
            o_seed = getattr(self,attr)
            o_targ = getattr(target,attr)
            if self.checkTouch(o_targ):
                o_res = o_seed.extrapolate_to(o_targ)
            else:
                o_res = o_targ.copy(enforce_rules = False)
                #if can't touch an attribute, copy the target wholesale
            setattr(result,attr,o_res)
        #
        #step 3: return container
        return result

    def fillOut(self,*tagsToOmit):
        """


        BusinessUnit.fillOut([*tagsToOmit]) -> None


        Will no-op if instance.filled is True. Otherwise, will first sync
        instance balance sheet, then consolidate, and finally derive. At
        conclusion, method sets instance.filled to True to make sure that
        subsequent calls do not increment existing values. 

        NOTE: consolidate() blocks derive() on the same lineitem.
        
        Once a non-None value is written into a Lineitem at one component,
        BusinessUnit.derive() will never run again for that LineItem, either at
        that component or any parent or ancestor of that component.
        """
        if self.filled:
            return
        else:
            self.consolidate(*tagsToOmit)
            self.derive(*tagsToOmit)
            self.financials.summarize()
            self.filled = True

    def fitToPeriod(self, timePeriod, recur = True, updateID = True):
        """


        BU.fitToPeriod(timePeriod[, recur = True]) -> None

        
        Method syncs instance.header.startDate and endDate with time period.
        Method then sets the namespace id for the instance to that of the period
        and the life.ref_date to the period endpoint. 

        If ``recur`` == True, repeats for each component.
        If ``updateID`` == True, method updates the instance id for the new
        namespace.
        """
        self.period = timePeriod
        self.header.startDate = timePeriod.start
        self.header.endDate = timePeriod.end
        self.id.setNID(timePeriod.id.namespace_id)
        if updateID:
            self.id.assignBBID(self.name)
        self.life.set_ref_date(timePeriod.end)
        if recur:
            #repeat all the way down to the ground floor
            for sub in self.components.getOrdered():
                sub.fitToPeriod(timePeriod, recur)

    def pretty_print(self,
                     top_element = "=",
                     side_element = "|",
                     box_width = 23,
                     field_width = 5):

        """


        BusinessUnit.pretty_print([top_element = "=" [,
                                  side_element = "|" [,
                                  box_width = 23 [,
                                  field_width = 5]]]]) -> list


        Method returns a list of strings that displays a box if printed in
        order. Line ends are naked (i.e, lines do **not** terminate in a
        new-line character).

        Box format (live units):
      
        +=====================+
        | NAME  : Baltimore-4 |
        | ID    : ...x65-0b78 |
        | DOB   :  2015-04-01 |
        | LIFE  :         43% |
        | STAGE :      MATURE |   
        | TYPE  :         OPS |
        | FILL  :        True |
        | COMPS :          45 |
        +=====================+

        Box format (dead units):

        +=====\========/======+
        | name \: Balt/more-4 |
        | id    \ .../65-0b78 |
        | dob   :\ 2/15-04-01 |
        | life  : \/      43% |
        | stage : /\   MATURE |   
        | type  :/  \     OPS |
        | fill  /    \   True |
        | comps/:     \    45 |
        +=====/========\======+

        Box format (unborn units):
      
        ?  = = = = = = = = =  ?
        | NAME  : Baltimore-4 |
          ID    : ...x65-0b78  
        | DOB   :  2015-04-01 |
          LIFE  :         43%  
        | STAGE :      MATURE |   
          TYPE  :         OPS  
        | FILL  :        True |
          COMPS :          45 
        ?  = = = = = = = = =  ?
        
        """
        reg_corner = "+"
        alt_corner = "?"
        alt_element = " "
        #
        ##formatting rules
        template = "%s %s : %s %s"
        empty_line = template % (side_element,
                                     ("x" * field_width),
                                     "",
                                     side_element)
        #empty_line should equal " | xxxxxxxx :  |"
        data_width = box_width - len(empty_line)
        #
        ##fields:
        fields = ["NAME",
                  "ID",
                  "DOB",
                  "LIFE",
                  "STAGE",
                  "TYPE",
                  "FILL",
                  "COMPS"]
        ##data
        data = {}
        data["NAME"] = str(self.name)[:data_width]
        #
        id_dots = "..."
        tail_width = data_width - len(id_dots)
        id_tail  = str(self.id.bbid)[(tail_width * -1):]
        data["ID"] = id_dots + id_tail
        #
        if self.life.date_of_birth:
            dob = self.life.date_of_birth.isoformat()
        else:
            dob = "n/a"
        data["DOB"] = dob
        #
        if self.life.percent is not None:
            life = int(self.life.percent)
            life = str(life) + r"%"
        else:
            life = "n/a"
        data["LIFE"] = life
        #
        stage = str(self.life.stage)[:data_width]
        data["STAGE"] = stage.upper()
        #
        unit_type = str(None)
        data["TYPE"] = unit_type.upper()
        #
        data["FILL"] = str(self.filled)
        #
        data["COMPS"] = str(len(self.components))
        #
        ##assemble the real thing
        ##DONT FORGET TO rjust(data_width)
        #
        lines = []
        top_border = reg_corner + top_element * (box_width - 2) + reg_corner
        lines.append(top_border)
        #
        for field in fields:
            new_line = template % (side_element,
                                   field.ljust(field_width),
                                   data[field].rjust(data_width),
                                   side_element)
            lines.append(new_line)
        #
        #add a bottom border symmetrical to the top
        lines.append(top_border)
        #
        #post-processing (dashed lines for units scheduled to open in the
        #future, x's for units that have already closed)
        #
        if self.life.ref_date < self.life.date_of_birth:
            #
            alt_width = int(box_width / 2) + 1
            alt_border = (top_element + alt_element) * alt_width
            alt_border = alt_border[:(box_width - 2)]
            alt_border = alt_corner + alt_border + alt_corner
            #
            core_lines = lines[1:-1]
            for i in range(0, len(core_lines), 2):
                line = core_lines[i]
                core_symbols = line[1:-1]
                line = alt_element + core_symbols + alt_element
                core_lines[i] = line
            #
            lines = [alt_border] + core_lines + [alt_border]
        #
        if self.life.dead:
            #
            alt_lines = []
            line_count = len(lines)
            down_start = int((box_width - line_count)/2)
            #X is line_count lines wide
            up_start = down_start + line_count
            #
            for i in range(line_count):
                #
                #replace the character at (down_start + i) with "\"
                #replace the character at (up_start - i) with "/"
                #
                line = lines[i]
                #
                down_pos = (down_start + i)
                seg_a = line[: (down_pos)]
                seg_b = line[(down_pos + 1):]
                line = seg_a + "\\" + seg_b
                #
                up_pos = (up_start - i)
                seg_a = line[:(up_pos)]
                seg_b = line[(up_pos + 1):]
                line = seg_a + "/" + seg_b
                #
                alt_lines.append(line)
            lines = alt_lines
        #
        return lines    

    def resetFinancials(self,recur = True):
        """


        BU.resetFinancials([recur = True]) -> None


        Method resets financials for instance and, if ``recur`` is True, for
        each of the components. Method sets instance.filled to False.
        """
        self.filled = False
        print("set ``filled`` to False for bbid\n%s\n" % self.id.bbid)
        self.financials.reset()
        if recur:
            for bu in self.components.getOrdered():
                bu.resetFinancials(recur)
                
    def setAnalytics(self,atx):
        """


        BU.addAnalytics(atx) -> None


        Method sets instance.analytics to passed-in argument, sets analytics
        object to point to instance as its parent. 
        """
        atx.setPartOf(self)
        self.analytics = atx

    def setComponents(self,comps = None):
        """


        BU.setComponents([comps = None]) -> None


        Method sets instance.components to the specified object, sets object to
        point to instance as its parent. If ``comps`` is None, method generates
        a clean instance of Components().
        """
        if not comps:
            comps = Components()
        comps.setPartOf(self)
        self.components = comps

    def setDrivers(self,dr_c = None):
        """


        BU.setDrivers([dr_c = None]) -> None


        Method for initializing instance.drivers with a properly configured
        DrContainer object. Method sets instance as the parentObject for
        DrContainer and any drivers in DrContainer.
        """
        if not dr_c:
            dr_c = DrContainer()
        dr_c.setPartOf(self, recur = True)
        self.drivers = dr_c

    def setFinancials(self, fins = None):
        """


        BU.setFinancials([fins = None]) -> None


        Method for initializing instance.financials with a properly configured
        Financials object.

        Method will set instance financials to ``fins``, if caller specifies
        ``fins``. Otherwise, method will set financials to a new Financials
        instance. 
        """
        if fins:
            self.financials = fins
        else:            
            self.financials = Financials()

    def updateDirectory(self, recur = True, overwrite = True):
        """


        BU.updateDirectory([recur = True[, overwrite = True]]) -> None


        Method updates the bu_directory on the instance period with the contents
        of instance.components (bbid:bu). If ``recur`` == True, repeats for
        every component in instance.

        If ``overwrite`` == False, method will raise an error if any of its
        component bbids is already in the period's bu_directory at the time of
        call.

        NOTE: Method will raise an error only if the calling instance's own
        components have ids that overlap with the bu_directory. To the extent
        any of the caller's children have an overlap, the error will appear only
        when the recursion gets to them. As a result, by the time the error
        occurs, some higher-level or sibling components may have already updated
        the period's directory.        
        """
        if not overwrite:
            if self.id.bbid in self.period.bu_directory:
                c1 = "TimePeriod.bu_directory already contains an object with "
                c2 = "the same bbid as this unit. \n"
                c3 = "unit id:         %s\n" % self.id.bbid
                c4 = "known unit name: %s\n"
                c4 = c4 % self.period.bu_directory[self.id.bbid].name
                c5 = "new unit name:   %s\n\n" % self.name
                print(self.period.bu_directory)
                c = c1+c2+c3+c4+c5
                raise BBExceptions.IDCollisionError(c)
            else:
                self.period.bu_directory[self.id.bbid] = self
        else:
            self.period.bu_directory[self.id.bbid] = self
        if recur:
            for C in self.components.getOrdered():
                C.updateDirectory(recur,overwrite)

    def verifyID(self, recur = True):
        """


        BU.verifyID([recur = True]) -> bool


        Method checks whether:
        
        (1) instance is in the same namespace id as its time period,
        (2) instance bbid is the correct uuid for an object with its name in the
            time period's name space, and
        (3) optionally, if ``recur`` == True, all business units in
            instance.components satisfy tests (1) and (2).

        Method returns True when all three prongs are True, False otherwise. 
        """
        result = True
        if self.period:
            if self.id.namespace_id != self.period.id.namespace_id:
                result = False
        if result:
            result = self.id.verify(self.name)
        if result and recur:
            for C in self.components.getOrdered():
                if not C.verifyID(recur=True):
                    result = False
                    break
                else:
                    continue
        return result

    
