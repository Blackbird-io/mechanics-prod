#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Tags
"""

Module defines Tags class and provides certain related functions.

NOTE: Class variables set at the bottom of the module (after class definition)

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
m_spacer_opt          string for Tags.spacer_opt
m_spacer_req          string for Tags.spacer_req
special_tags          list of special extrapolation triggers
m_hands_off           list of tags that prohibit modification altogether

FUNCTIONS:
deCase()              local rebinding for Tools.Parsing.deCase

CLASSES:
Tags                  mix-in class that provides tagging, naming, and belonging
====================  ==========================================================
"""




#imports
import copy

from Managers.tag_manager import loaded_tagManager as tag_manager
from Tools.Parsing import deCase




#globals
m_spacer_opt = tag_manager.catalog["BLACKBIRDSTAMP"]+"end own optionalTags"
m_spacer_req = tag_manager.catalog["BLACKBIRDSTAMP"] + "endRequiredTags"
special_tags = [tag_manager.catalog["special_ex"],
                tag_manager.catalog["special_ex"].casefold(),
                tag_manager.catalog["hardcoded"],
                tag_manager.catalog["hardcoded"].casefold(),
                tag_manager.catalog["do not touch"],
                tag_manager.catalog["do not touch"].casefold()]
m_hands_off = [tag_manager.catalog["do not touch"],
               tag_manager.catalog["do not touch"].casefold()]
m_hands_off = set(m_hands_off)

doNotTouchTag = tag_manager.catalog["do_not_touch"]
dropDownReplicaTag = tag_manager.catalog["ddr"]

#classes
#NOTE: Class variables set at the bottom of the module (after class definition)

class Tags:
    """

    Object that carries identifying tags throughout the Blackbird environment.

    Tags are stored in two lists: ``required`` and ``optional``. Lists may
    overlap and may contain items more than once.

    Matchmaking functions (external to a BusinessUnit) MUST match ALL
    ``required`` tags to a target object.

    Matchmaking functions (external to a BusinessUnit) do not have to
    match any of the ``optional`` tags for the match to be valid.
    
    New tags are added to the optional list by default. Removing a tag from an
    object removes it from both required and optional lists simultaneously.

    Each Tags object has two special tags: ``name`` and ``partOf``.
    
    Both special tags are also dynamic attributes of each Tags object. Special
    tags should be modified through their respective attributes (Tags.name or
    Tags.partOf) or associated methods.

    The "name" tag is stored in requiredTags[0]; the object's name is the value
    of requiredTags[0]. The "partOf" tag is stored in requiredTags[1] and
    references the name of the parentObject.

    If a Tags object specifies a parentObject, the instance's
    dynamicSpecialTagManager will **always** overwrite reqTags[1] with the
    parent's name. The descriptor will allow direct changes to .partOf, but
    immediately "forget" them following a call to the attribute. To permanently
    alter the value of .partOf, set .parentObject to None. 

    NOTE: Direct changes to requiredTags[:2] (instance-level state for ``name``
    ``partOf``) are not recommended.

    Instance.partOf may not be especially informative on it's own, since the
    container object (``parentObject``) may not have a name attribute. Even if
    the container does have a name attribute, it may be difficult to locate by
    using that attribute. For that reason, instance.parentObject stores a
    pointer to the parentObject directly.
    
    NOTE: instance.parentObject may be an object OTHER THAN THE DIRECT CONTAINER
    of the instance. For example, in standard usage, a BusinessUnit will store
    Drivers in self.Drivers. The .parentObject attribute for each driver in such
    a case would be set to the BusinessUnit, not BusinessUnit.Drivers. The
    higher-level hook providers the Driver with easy access to BU.financials and
    any other attributes it may need for computation. A hook to
    BusinessUnit.Drivers would not effectively accomplish that goal.    

    For both ``name`` and ``partOf``, the dynamicSpecialTagManager descriptor
    routes gets and sets of the attribute to the right slot in requiredTags. The
    descriptor also transforms deletions of ``name`` and ``partOf`` attributes
    to None values in the proper positions of requiredTags.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _inheritedTags        list; stores tags instance inherited from other objs
    _optionalTags         list; tags applied to instance
    allTags               list; dynamic, returns requiredTags+optionalTags
    autoRegister          bool; CLASS attr, whether tag() should add to catalog
    tagManager            obj; CLASS pointer to tagManager object
    connected             bool; CLASS, True if connected to a tagManager
    hands_off             list; CLASS, tags that prohibit any modification
    name                  name of instance, dynamic, value of requiredTags[0]
    optionalTags          list; dynamic, returns _optionalTags + _inheritedTags 
    parentObject          obj; points to any obj passed in to setPartOf()
    partOf                name of parent, dynamic, value of reqTags[1]
    reg_req               bool; CLASS, if False won't apply tags not in catalog
    requiredTags          list; tags required for matching
    spacer_req            string; CLASS, separates req tags from optional in all 
    spacer_opt            string; CLASS, separates _opt from _inh tags in opt
    spec_tags             list; CLASS, tags that trigger special extrapolation
    tagSources            list; CLASS, attributes from which obj inherits tags
    
    
    FUNCTIONS:
    disconnect            CLASS METHOD: unhooks Tag objects from tagManager
    class dyn_OptTManager descriptor for ``optionalTags``
    class dyn_AllTManager descriptor for ``allTags``
    class dyn_SpecTManager  descrptor for ``name`` and ``partOf``
    checkOrdinary()       returns True iff target has no spec_tags
    checkTouch()          returns True iff target has no hands_off tags
    clearInheritedTags()  sets ._inh to an empty list
    copy()                returns a copy of an object with own tag lists
    copyTagsTo()          changes target tags to a copy of self tags
    copyTagsTo_rules_on() applies tags while following tagManager.rules
    copyTagsTo_rules_off()  applies tags while ignoring tagManager.rules
    extrapolate_to()      generates a copy of target w updated tags
    ex_to_default()       returns a Tags.copy() 
    ex_to_special()       creates a Tags.copy(), adds source tags
    inheritTags()         inherits tags from every attribute named in tagSources
    inheritTagsFrom()     adds tags on a different object to instance
    reg_req_on()          sets class to require tag registration before tagging
    reg_req_off()         sets class to permit unregistered tagging
    registerTag()         registers tag in tag catalog
    setTagManager()       CLASS; sets pointer to tag manager
    setName()             sets instance.reqTags[0]
    setPartOf()           sets partOf and parentObject relationships
    tag()                 adds tag to object, if parameters allow
    unTag()               removes all instances of tag from object
    ====================  ======================================================
    """
    #class attributes:
    #irrelevantAttributes = ["parentObject"]
    autoRegister = True
    tagManager = None
    connected = False
    hands_off = None
    reg_req = False
    spacer_opt = m_spacer_opt
    spacer_req = m_spacer_req
    spec_tags = None
    tagSources = []
    #tagSources must be a class attribute to make sure running Tags.__init__ on
    #descendant classes like BusinessUnit does not block their class-level
    #tagSources. Alternatively, would have to add tagSources as instance-level
    #data in the child classes.
   
    @classmethod
    def disconnect(cls):
        """


        Tags.disconnect() -> obj


        CLASS METHOD

        Disconnects class attributes that point at module objects. Simplifies
        serialization.

        Method returns the object that Tags.tagManager pointed to prior to call and
        toggles Tags.connected to False. 

        Attributes set to None:
        -- Tags.tagManager
        """
        old_man = cls.tagManager
        cls.tagManager = None
        cls.connected = False
        return old_man
    
    @classmethod
    def reg_req_off(cls):
        """


        Tags.reg_req_off -> None


        CLASS METHOD

        Method sets class.reg_req to False.
        """
        cls.reg_req = False

    @classmethod
    def reg_req_on(cls):
        """


        Tags.reg_req_on -> None


        CLASS METHOD

        Method sets class.reg_req to True.
        """
        cls.reg_req = True

    @classmethod
    def setTagManager(cls,ct):
        """


        Tags.setTagManager(ct) -> None


        CLASS METHOD

        Method sets pointer for class attribute ``tagManager`` and toggles
        Tags.connected to True.
        """
        cls.tagManager = ct
        cls.connected = True

    @classmethod
    def setHandsOff(cls,tho):
        """


        Tags.setHandsOff(tho) -> None


        CLASS METHOD

        Method sets class value for hands_off to specified list of tags. 
        """
        cls.hands_off = tho
    
    @classmethod
    def setSpecialTags(cls,sts):
        """


        Tags.setSpecialTags(sts) -> None


        CLASS METHOD

        Method sets Tags.spec_tags to argument. ``spec_tags`` serves as the list
        of triggers for special extrapolation. 
        """
        cls.spec_tags = sts  
    
    def __init__(self, name = None, parentObject = None):
        self._inheritedTags = []
        self._optionalTags = []
        self.parentObject = None
        self.requiredTags = [None,None]
        #self.name is requiredTags[0] and self.partOf is requiredTags[1] so list
        #should have minimum length of 2; actual values set through methods
        #
        self.setName(name)
        if parentObject:
            self.setPartOf(parentObject)

    class dyn_OptTManager:
        """

        Descriptor class that compiles and returns a list of optional tags on an
        instance. On __get__, class returns a list of optional and inherited
        tags on an instance, separated by a spacer.       
        """  
        def __get__(self,instance,owner):
            oTags = instance._optionalTags + [instance.spacer_opt]
            oTags = oTags + instance._inheritedTags
            return oTags

        def __set__(self,instance,value):
            c = "Direct write to ``optionalTags`` prohibited."
            raise BBExceptions.ManagedAttributeError(c)
    #dynamic class attribute:
    optionalTags = dyn_OptTManager()

        
    class dyn_AllTManager:
        """

        Descriptor class that compiles and returns a list of all tags on an
        instance.        
        """            
        def __get__(self, instance, owner):
            allTags = instance.requiredTags + [instance.spacer_req]
            allTags = allTags + instance.optionalTags
            return allTags

        def __set__(self,instance,value):
            c = "Direct write to ``allTags`` prohibited."
            raise BBExceptions.ManagedAttributeError(c)
    #allTags is a Tags class attribute managed by the descriptor above
    allTags = dyn_AllTManager()

    class dyn_SpecTManager:
        """

        Descriptor class that returns values for instance.name and instance.partOf.
        Descriptor also writes new values to requiredTags at the appropriate index.
        On deletion, replaces the special tags with None objects in requiredTags.

        For .partOf gets, the descriptor first checks if the caller has a
        .parentObject. If so, the descriptor updates caller.requiredTags[1] with the
        parentObject's name. The descriptor assumes name is None if the parentObject
        is missing the attribute. In all scenarios, the descriptor then returns
        whatever is in requiredTags[1].

        The descriptor permits .partOf sets to a specific value. Such sets should be
        paired with a deletion of the caller.parentObject. Direct sets of ``partOf``
        may erase a difficult-to-trace reference. If caller retains .parentObject,
        the first get of caller.partOf will overwrite the last set. 
        """       
        def __init__(self, targetAttribute):
            self.target = targetAttribute

        def __get__(self,instance,owner):
            if self.target == "name":
                return instance.requiredTags[0]
            elif self.target == "partOf":
                if instance.parentObject:
                    #if instance has a parentObject
                    #update requiredTagd[1] to parentObject's name or None
                    instance.requiredTags[1] = getattr(instance.parentObject,"name",None)
                #in any event, return requiredTags[1]
                return instance.requiredTags[1]

        def __set__(self,instance,value):
            if self.target == "name":
                instance.requiredTags[0] = value
            elif self.target == "partOf":
                instance.requiredTags[1] = value

        def __delete__(self,instance):
            if self.target == "name":
                instance.requiredTags[0] = None
            elif self.target == "partOf":
                instance.requiredTags[1] = None

    #Tags.name and Tags.partOf are dynamic class attributes linked to
    #self.requiredTags and managed by the descriptor above
    name = dyn_SpecTManager(targetAttribute = "name")
    partOf = dyn_SpecTManager(targetAttribute = "partOf")

    def checkOrdinary(self,target = None):
        """


        Tags.checkOrdinary([target = None]) -> bool


        Returns True if target is ordinary, False if it has any tags in
        instance.spec_tags.

        If ``target`` is left blank, method runs test on self.

        NOTE: Method compares target against **caller's** spec_tags.

        Tags objects use checkOrdinary() to select the appropriate type of
        extrapolate (or other) processing for a target object. By using the
        caller instance's attribute as the standard, method allows objects to
        evaluate targets with missing or outdated spec_tags. 
        """
        if not target:
            target = self
        result = False
        if set(self.spec_tags) & set(target.allTags) == set():
            result = True
        return result
    
    def checkTouch(self,target = None):
        """


        Tags.checkTouch([target = None]) -> bool


        Method returns True if target does not have any tags stored in
        instance.hands_off (e.g., do_not_touch), False otherwise.

        If ``target`` is left blank, method runs test on self.
        
        NOTE: Method compares target against **caller's** hands_off.

        Tags objects use checkTouch() to select the appropriate type of
        extrapolate (or other) processing for a target object. By using the
        caller instance's attribute as the standard, method allows objects to
        evaluate targets with missing or outdated hands_off lists. 
        """
        if not target:
            target = self
        result = False
        if set(self.hands_off) & set(target.allTags) == set():
            result = True
        return result
        
    def clearInheritedTags(self, recur = False):
        """


        Tags.clearInheritedTags([recur = True]) -> None


        Method sets instance._inheritedTags to an empty list.

        If ``recur`` is True, method calls clearInheritedTags(recur=True) on
        every attribute in instance.tagSources.
        """
        self._inheritedTags = []
        if recur:
            for attr in self.tagSources:
                obj = getattr(self,attr)
                obj.clearInheritedTags(recur = True)

    def copy(self,enforce_rules = True):
        """


        Tags.copy([enforce_rules = True]) -> obj


        Method returns a shallow copy of the instance. If ``enforce_rules`` is
        True, copy follows ``out`` rules. 
        """
        result = copy.copy(self)
        Tags.copyTagsTo(self,result,enforce_rules)
        return result
        
    
    def copyTagsTo(self,target,enforce_rules = True):
        """


        Tags.copyTagsTo(target[, enforce_rules = True]) -> None

        NOTE: Method changes target **in place**.
        
        Method copies tags from instance to target, attribute by attribute.
        Method delegates all actual work to either copyTagsTo_rules_on or
        copyTagsTo_rules_off.
        
        If ``enforce_rules`` == True, method follows the ``out`` rules of
        inheritance for each tag.

        NOTE2: Method may loop indefinitely if tagManager.rules contains
        circular references.
        """
        if self.tagManager.rules:
            self.copyTagsTo_rules_on(target)
        else:
            self.copyTagsTo_rules_off(target)

    def copyTagsTo_rules_on(self,target):
        """


        Tags.copyTagsTo_rules_on(target) -> None


        NOTE: Method changes target **in place**.

        Method replaces all tag attributes on target with copies of the
        respective attribute on the calling instance. Method follows tag rules
        where specified. Method preserves target.requiredTags[:2] (``name`` and
        ``partOf``).

        NOTE2: Method may loop indefinitely if tagManager.rules contains
        circular references.
        """
        fields = ["requiredTags","_optionalTags","_inheritedTags"]
        rules = self.tagManager.rules
        for attr in fields:
            t_field = None
            source_tags = getattr(self,attr)
            if attr == "requiredTags":
                t_field = "req"
                source_tags = source_tags[2:]
                preserve = getattr(target,attr)[:2]
                #Upgrade-S: can do a direct call instead of getattr
            else:
                if attr == "._inheritedTags":
                    t_field = "inh"
            check_tags = set(source_tags) & set(rules.keys())
            #
            setattr(target,attr,[])
            #make independent blank lists for the target to make sure method
            #doesn't accidentally modify source attributes (ie, when it is
            #called as part of Tags.copy)
            #
            new_tags = getattr(target,attr)
            if attr == "requiredTags":
                new_tags.extend(preserve)
                #preserve target name, partOf
            #
            for t in source_tags:
                if t in check_tags:
                    #t has a rule
                    if rules[t]["out"].place:
                        new_tags.append(t)
                        #only add rules-based tags if the rules says its ok
                    if rules[t]["out"].cotag:
                        cotags = rules[t]["out"].cotag
                        target.tag(cotags,field = t_field, mode = "at")
                        #need to use Tags.tag() in case cotags have to get
                        #registed or lead to more cotags. mode is "at" because
                        #the tag that requires cotags is on the lineitem already
                        #(ie, "at" the same object). 
                    if rules[t]["out"].detag:
                        for lessT in rules[t]["out"].detag:
                            target.unTag(lessT)
                else:
                    #t does not have a rule
                    new_tags.append(t)
            
    def copyTagsTo_rules_off(self,target):
        """


        Tags.copyTagsTo_rules_on(target) -> None


        NOTE: Method changes target **in place**.

        Method replaces all tag attributes on target with copies of the
        respective attribute on the calling instance. Method preserves
        target.requiredTags[:2] (``name`` and ``partOf``).
        """
        target.requiredTags = target.requiredTags[:2] + self.requiredTags[2:]
        #preserve **target** name, partOf, supplement w seed req tags
        target._optionalTags = self._optionalTags[:]
        target._inheritedTags = self._inheritedTags[:]
    
    def extrapolate_to(self,target):
        """


        Tags.extrapolate_to(target) -> obj


        Method provides basic selection logic and standard interface for
        extrapolation.

        Extrapolation is the process of defining an object's state at a point in
        time from (i) the same object's state at a prior point in time (the seed
        object) and (ii) optionally, the object's **prior** state at the target
        point in time (the target object).

        This Method delegates all actual extrapolation work to instance
        subroutines. The subroutines are either Tags methods or any redefinition
        thereof at a descendant class level. Method returns subroutine output.

        Method runs target.inheritTags() before selecting a subroutine. 

        Default subroutine:
           instance.ex_to_default(target)

        Alternative subroutine (for targets with a tag in Tags.spec_tags):
           instance.ex_to_special(target)
  
        Most objects specify their own, type-specific extrapolation rules.
        Extrapolation routines can be a simple copy for time-insensitive objects
        with no contents, or they can be complex attribute-by-attribute assembly
        processes.        
        """
        #always returns a new object
        result = None
        target.inheritTags(recur = True)
        if self.checkOrdinary(target):
            result = self.ex_to_default(target)
        else:
            result = self.ex_to_special(target)
        return result    

    def ex_to_default(self,target):
        """


        Tags.ex_to_default(target) -> object


        Method provides most basic extrapolation method. Method returns a
        self.copy(enforce_rules = True) of the target. Points to Tags.copy()
        or a lower-level .copy() definition. 
        """
        result = self.copy(enforce_rules = True)
        return result
        
    def ex_to_special(self,target,mode = "at"):
        """


        Tags.ex_to_special(target[, mode = "at"]) -> obj


        Method provides a way to cross-pollinate tags between objects. Method
        returns a shallow copy of the seed (caller) instance. The seed tags,
        after passing through rules, provides the template. The method
        then adds new tags from target one field at a time (new items in
        target._optionalTags go on result._optionalTags).
        
        Method does not look at target.requiredTags[:2]. Method applies target
        tags in sorted() order.

        The optional ``mode`` argument describes the set of rules Tags.tag()
        applies when moving target tags to result.
        """
        seed = self
        result = Tags.copy(seed,enforce_rules = True)
        #maintain all tags on seed
        fields = ["requiredTags","_optionalTags","_inheritedTags"]
        for attr in fields:
            targ_tags = getattr(target,attr)
            if attr == "requiredTags":
                targ_tags = targ_tags[2:]
            targ_tags = set(targ_tags)
            r_res_tags = getattr(result,attr)
            res_tags = set(r_res_tags)
            new_tags = targ_tags - res_tags
            new_tags = sorted(new_tags)
            #sort the new tags into a stable order to ensure consistency across
            #runtime
            result.tag(*new_tags,field = attr, mode = mode)
        return result

    def inheritTags(self, recur = True):
        """


        T.inheritTags([recur = True]) -> None


        Method runs instance.inheritTagsFrom() every object whose attribute
        name is stored in tagSources.

        If ``recur`` == True, method runs inheritTags() on every source object
        before passing it to the instance. We recommend running the method with
        recurison in normal operation to ensure that each object gets the most
        fresh set of tags possible.

        Method will generate AttributeErrors if a source attribute does not
        support a Tags interface. 
        """
        for attr in self.tagSources:
            source = getattr(self,attr)
            if source:
                if recur:
                    source.inheritTags(recur = True)
                self.inheritTagsFrom(source)        

    def inheritTagsFrom(self,source,*doNotInherit, noDuplicates = True):
        """


        Tags.inheritTagsFrom(source,*doNotInherit[,noDuplicates = True]) -> None


        Method adds tags found on the source to self as inherited tags. Method
        skips source.requiredTags[:2] (name and partOf). 
        
        The method will not copy ``doNotInherit`` tags. By default, if
        doNotInherit is blank, method will strip out doNotTouchTag and
        dropDownReplicaTag (replicas are a phenomenon of local context, thus
        it's inappropriate to apply them elsewhere). 

        If ``noDuplicates`` is True, method will not copy any source tags that
        the instance already carries. In this mode, a SINGLE existing tag will
        block inheritance of ALL matching objects.
        
        If ``noDuplicates`` is False, method will copy all source tags as is.
        That is, the instance and source occurrences will be additive.

        This method evaluates tags as casefolded objects to the extent possible.
        """
        sourceTags = source.requiredTags[2:] + source.optionalTags[:]
        dni = [doNotTouchTag, dropDownReplicaTag]
        if doNotInherit != tuple():
            dni = doNotInherit
        if noDuplicates:
            sourceTags = set(sourceTags) - set(self.allTags)
        #source tags is now **unordered**
        sourceTags = sourceTags - set(dni)
        sourceTags = sorted(sourceTags)
        #turn sourceTags into a sorted list to make sure tags are always added
        #in the same order; otherwise, pseudo-random order of tags in a set
        #wrecks HAVOC on comparisons
        self.tag(*sourceTags, field="inh", mode="up")
        #NOTE: can preserve order by expanding dni and go through tags one by
        #one. dni = set(dni)+set(self.allTags). if tag in dni: pass, else tag()

    def registerTag(self,tag):
        """


        Tags.registerTag(tag) -> None


        Method registers cased and caseless versions of the tag in the tag
        catalog. Delegates all processing to tagManager. 
        """
        alt = deCase(tag)
        self.tagManager.registerTag(tag)
        self.tagManager.registerTag(alt)

    def setName(self, newName):
        """


        T.setName(newName) -> None


        Method for setting the name of an object.

        The name specified via this method is set as the object's name attribute
        and recorded in object.requiredTags[0].
        
        All "names" in the Blackbird environment are required tags.
        If a suitor object specifies a name condition, a target object must have
        an identical name to be a match.

        Names are distinct from other required tags in that within a given
        container, names should generally be unique. That is, a given container
        object should generally contain one object with a specific name. By
        contrast, a container object may contain multiple objects with identical
        other requiredTags (requiredTags[2:]). The decision of whether to follow
        the unique name policy is left to higher-level objects. Common
        exceptions include Financials objects, which create replicas with
        identical names to manage certain records. 

        Names are stored in the first position of requiredTags and managed
        through the dynamicSpecialTagManager descriptor. Names are optional. If
        no name is specified, the requiredTags[0] position will be filled with a
        None object. Deleting a name similarly sets requiredTags[0] to None.
        """
        self.name = deCase(newName)

    def setPartOf(self, parentObject):
        """


        T.setPartOf(parentObject) -> None


        This method sets an instance's ``partOf`` and ``parentObject``
        attributes.

        If the parentObject provided to the method has a name, instance.partOf
        is set to the same value. If the parentObject does not have a name,
        method sets instance.partOf to None. In both cases, method sets
        instance.parentObject to point to the actual parentObject.
        """
        if getattr(parentObject,"name",None):
            self.partOf = deCase(parentObject.name)
        else:
            #get here if parentObject doesn't have a name attribute or if it's
            #name is None
            self.partOf = None
        self.parentObject = parentObject        

    def tag(self,
            *newTags,
            field = "opt",
            mode = "at",
            permit_duplicates = False):
        """


        Tags.tag(*newTags[,field = "opt"[, mode = "at"]]) -> None


        Method appends tags to an instance.

        NOTE: Method automatically **decases** all tags.
        
        The ``field`` argument regulates tag placement on the instance:
        -- "req" means last position of instance.requiredTags
        -- "opt" [ default ] means last position of instance._optionalTags
        -- "inh" means last position of instance._inheritedTags
        
        Tags should generally be optional. When in doubt, add more tags.

        NOTE2: An instance's ``name`` and ``partOf`` are set directly via a
        descriptor. These tags always skip catalog registration.
        
        For tags registered to a rule in the catalog, ``mode`` controls which
        rule the method follows: 
        -- "at" [ default ] means tagging is taking place within the same object
        -- "up" means tagging is taking place during inheritance
        -- "out" means tagging is taking place during copying.

        NOTE3: Use of detag() rules is highly discouraged.

        For best results, create independent functions that explicitly define
        scenarios during which a tag should be removed or replaced. 

        Rule[x].detag rules apply only to tags "behind" them. As such, the
        impact of detag rules varies based on the state of an object's tags
        at the time Tags.tag() encounters the detag trigger. Tags.tag() applies
        detag rules as soon as it encounters their trigger tag. At that time,
        the instance may not have all of the tags the creator of the detag rule
        expects it to have. For example, the instance could be inheriting tags
        after they have been sorted from a set. The order of these tags during
        inheritance could thus differ from the order on the seed object.
        Application of a detag rule to a pure deepcopy of the seed object could
        then yield a different outcome than its application during normal
        tagging.        
        """
        attrs = {}
        attrs["r"]=attrs["req"]=attrs["required"]="requiredTags"
        attrs["o"]=attrs["opt"]=attrs["optional"]="_optionalTags"
        attrs["i"]=attrs["inh"]=attrs["inherited"]="_inheritedTags"
        attrs[0] = attrs["requiredTags"] = attrs["r"]
        attrs[1] = attrs["_optionalTags"] = attrs["o"]
        attrs[2] = attrs["_inheritedTags"] = attrs["i"]
        #
        real_thing = getattr(self,attrs[field])
        #
        for tag in newTags:
            #
            #
            #NOTE: automatically decase tags!
            tag = deCase(tag)
            #
            #filter out duplicates if necessary
            if permit_duplicates:
                pass
            else:
                if tag in self.allTags:
                    continue               
            #
            registered = False
            if self.tagManager:
                if tag in self.tagManager.catalog.keys():
                    registered = True
            if registered:
                #processing for registered tags                    
                if tag not in self.tagManager.rules.keys():
                    real_thing.append(tag)
                    #plain vanilla tag
                else:
                    rule = self.tagManager.rules[tag][mode]
                    if rule.place:
                        real_thing.append(tag)
                    if rule.cotag:
                        for moreT in rule.cotag:
                            self.tag(moreT,field,mode)
                    if rule.detag:
                        for lessT in rule.untag:
                            self.unTag(tag)
                            #untags are dependent on tags already in place
                            #those tags may vary due to sorting
                            #should generally disallow & require manual
            else:
                #processing for unregistered tags
                if self.reg_req == True:
                    c = "'%s' is not a registered tag. " % tag
                    c = c + "Registration required for tagging."
                    raise BBExceptions.TagRegistrationError(c)
                else:
                    if self.tagManager and self.autoRegister:
                        self.registerTag(tag)
                    #tag not registered, but that's ok, just append it
                    real_thing.append(tag)
            
    def unTag(self,badTag,checkInherited = True):
        """


        Tags.unTag(badTag) -> None

        
        Method to remove tags from an instance. 

        If badTag is located in requiredTags[0] or requiredTags[1], method
        replaces the badTag with None. Method calls itself upon finding and
        removing the first iteration of the badTag to check for any others.

        If ``checkInherited`` == True, method will remove the badTag from the
        instance's ._inheritedTags. 
        """
        #have to nest the recursive call in the if statements, otherwise method
        #will loop indefinitely. that is, only call the method again if the
        #badTag was already found once and removed
        if badTag in self.requiredTags[:2]:
            location = self.requiredTags.index(badTag)
            self.requiredTags[location] = None
            self.unTag(badTag)
        else:
            pass
        if badTag in self.requiredTags[2:]:
            self.requiredTags.remove(badTag)
            self.unTag(badTag)
        else:
            pass
        if badTag in self._optionalTags:
            self._optionalTags.remove(badTag)
            self.unTag(badTag)
        else:
            pass
        if checkInherited:
            if badTag in self._inheritedTags:
                self._inheritedTags.remove(badTag)
                self.unTag(badTag)
            else:
                pass
        else:
            pass

#
Tags.setHandsOff(m_hands_off)
Tags.setSpecialTags(special_tags)
Tags.setTagManager(tag_manager)
#
