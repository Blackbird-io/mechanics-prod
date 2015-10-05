#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.driver
"""

Module defines Driver class. Drivers modify LineItems. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Driver                objects that modify lineitems from inside business units
====================  ==========================================================
"""



 
#imports
import copy
import time

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.system.bbid import ID
from data_structures.system.tags import Tags
from content import formula_manager as FormulaManager
#import FormulaManager; will connect the module to the Driver class at the
#bottom (after class definitions). Driver class will then be able to access the
#formula catalog

from .auto_align import AutoAlign
from .equalities import Equalities




#globals
#n/a

#classes
class Driver(Tags, AutoAlign):
    """

    Drivers apply formulas to business units.

    1) Each Driver applies one and only one formula. 

    A Driver may apply the formula whenever the Driver works on a LineItem
    that satisfies that Driver instance's workConditions. 

    To limit the size of extrapolated models, a Driver instance stores
    only a bbid for its formula, not the formula itself. When the Driver
    has to work, the Driver retries the formula from the formula catalog
    (managed by FormulaManager) and applies it to the relevant line and
    business unit. 

    When the Driver calls a formula, the Driver provides the formula with
    the target LineItem, the Driver's parentObject and signature, and an
    arbitrary set of additional work parameters stored in Driver.data. 

    Formulas generally compute the value of one LineItem based on data from
    other LineItems or BusinessUnit attributes.

    2) Drivers work only on objects that satisfy that instance's workConditions.

    Drivers require the target object tags to contain **ALL** values specified
    in each workConditions key. A Driver does NOT require that the object
    contain ONLY the items specified in workConditions.

    Setting the value for a workCondition key to None means that all objects
    will match it. In other words, None is the absence of a workCondition. 

    3) A BusinessUnit may contain several different Drivers applicable to a
    given line. In such an event, a BusinessUnit will construct a queue of
    Drivers for the lineItem prior to running them. Drivers signal where they
    should appear in queue through AutoAlign attributes.
    
    Queues should generally be limited to 5 drivers per line. 
    
    For more information, see the doc string for AutoAlign and Queue classes, as
    well as BusinessUnit.derive().

    4) A Topic should provide the Driver with a signature prior to injecting the
    Driver into a BusinessUnit. The driver signature should contain the Topic's
    descriptive information. Driver signatures should be informative to both
    machine and human readers.

    5) A Topic should assign the driver an id within the Topic's namespace.
    BusinessUnits won't add a driver if the BU already contains a driver with
    the same id.

    6) Topics and other modules should store any model-specific data used by 
    the driver's formula in the driver's ``data`` dictionary. For example, if a
    formula relies on average ticket price to compute revenue, ``data`` should
    contain something like "atp" : 4.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    
    DATA:
    active                bool; is instance turned on 
    data                  dict; place holder for driver-specific data
    id                    instance of ID
    FM                    class; pointer to formula manager 
    formula_bbid          bbid for formula that Driver applies
    signature             string; how the driver signs lines it modifies
    workConditions        dict; criteria for objects driver will process

    FUNCTIONS:
    __eq__                True for objects with the same work function              
    __ne__                returns bool negative of __eq__
    __hash__              returns hash of instance bbid, raises error if blank
    canWorkOnThis()       returns bool if line satsifies work conditions
    copy()                returns a new instance w own objects in key places
    configure()           set data and formula on instance in order
    disconnect()          CLASS method, sets FM pointer to None
    setData()             sets instance.data to deep copy of argument
    setFormula()          sets instance work function to argument (for hash)
    setFormulaManager()   CLASS method, sets FM pointer to new object
    setSignature()        sets instance signature to object
    setWorkConditions()   sets conditions for suitable objects
    workOnThis()          gets and runs formula with instance data and sig
    ====================  ======================================================
    """
    FM = None

    @classmethod
    def disconnect(cls):
        cls.FM = None
    
    @classmethod
    def setFormulaManager(cls,new_FM):
        cls.FM = new_FM
        
    def __init__(self, signature = None):
        Tags.__init__(self)
        AutoAlign.__init__(self)
        #
        self.active = True
        self.data = {}
        self.formula_bbid = None
        self.id = ID()
        #specific uuid assigned when TopicManager configures topic catalog,
        #based on driver's name in topic's namespace id
        self.signature = signature
        self.workConditions = {}
        self.workConditions["name"] = ["FAIL"]
        self.workConditions["partOf"] = ["FAIL"]
        self.workConditions["allTags"] = ["FAIL"]
        #set condition values to a default that must be overwritten to make sure
        #default configuration doesnt apply to every lineItem.

    def __eq__(self, comp, trace = False, tab_width = 4):
        """


        Driver.__eq__(comp) -> bool


        Method returns True if instance and comp hash the same, False otherwise.
        """
        result = False
        if hash(self) == hash(comp):
            result = True
        return result

    def __ne__(self, comp, trace = False, tab_width = 4):
        """


        Driver.__ne__(comp) -> bool


        Method returns boolean negative of __eq__.
        """
        result = not self.__eq__(comp, trace, tab_width)
        return result
    
    def __hash__(self):
        """


        Driver.__hash__() -> obj


        Method returns the hash of the instance's bbid. 
        """
        if not self.id.bbid:
            c1 = "Driver.id.bbid blank. Driver expected to have filled bbid at"
            c2 = "runtime."
            c = c1 + c2
            raise BBExceptions.IDAssignmentError(c)
        return hash(self.id.bbid)
    
    def canWorkOnThis(self,targetLineItem):
        """


        Driver.canWorkOnThis(targetLineItem) -> bool


        This method checks whether the targetLineItem satisfies workConditions.
        If the targetLineItem satisfies each of the workConditions specified for
        the instance, the method returns True. Otherwise, the method returns
        False.

        To satisfy the allTags condition, an object must carry each tag in
        instance.workConditions["allTags"] (ie, instance.wC[allTags] must be
        a subset of target.allTags). 

        NOTE: driver.workConditions keys may include None as values to indicate
        absence of a constraint. Accordingly, match is evaluated against
        candidate attributes plus a None element.

        A workCondition with a value equal to None or an empty list will be
        satisfied for all lineItems.
        """
        #must be careful not to split strings (names) into letters with set()
        if not set(self.workConditions["name"]).issubset([targetLineItem.name]+[None]):
            return False
        else:
            if not set(self.workConditions["partOf"]).issubset([targetLineItem.partOf]+[None]):
                return False
            else:
                if not set(self.workConditions["allTags"]).issubset(targetLineItem.allTags + [None]):
                    return False
                else:
                    return True
        
    def configure(self, data, formula):
        """


        Driver.configure(data, formula) -> None


        Method configures instance in proper order: first sets data using
        setData(), then sets formula using setFormula(). The second step
        validates formula against instance data. Use this method to avoid
        errors in topics.         
        """
        self.setData(data)
        self.setFormula(formula)
        
    def copy(self,enforce_rules = True):
        """


        Driver.copy([enforce_rules = True]) -> Driver


        Method returns a new Driver object. Result is a shallow copy of instance
        except for the following attributes, which are deep:

        -- data
        -- workConditions

        Original object copies tags to result using Tags.copyTagsTo(), so method
        will enforce tag rules when specified.

        Result.parentObject points to the same object as original because the
        default shallow copy runs on the ``parentObject`` attribute.

        NOTE: Result points to same object as original on ``id`` and
        ``formula_bbid``. Therefore, the result should continue to point to the
        same formula even if that formula's id changes in place. The result
        should also track any in-place changes to original's id (e.g., change
        in namespace).
        """
        result = copy.copy(self)
        Tags.copyTagsTo(self,result,enforce_rules)
        result.data = copy.deepcopy(self.data)
        result.workConditions = copy.deepcopy(self.workConditions)
        return result

    def setData(self,new_data):
        """


        Driver.setData(new_data) -> None


        Method updates instance ``data`` dictionary with a deep copy of
        new_data.
        """
        new_data = copy.deepcopy(new_data)
        self.data.update(new_data)
        
    def setFormula(self,F):
        """


        Driver.setFormula(F) -> None


        Sets instance.formula_bbid to that of the argument. Method first checks
        if instance data includes all parameters required by formula.

        Method raises a DefinitionError if one of the parameters is missing.
        Topics may inject drivers into business units at time A with the
        intent that these drivers work only at some future time B (when their
        work conditions or other logic has been satisfied). Time B may be
        arbitrarily far away in the future. This method looks to avoid
        confusing future errors by making sure that the Topic author is aware
        of the required formula parameters at the time the Topic runs.
        
        Method also raises a DefinitionError if F does not have a bbid.

        NOTE: Method sets ``formula_id`` to point to the actual formula's id
        object. As such, Driver instance should continue referencing the same
        formula object if it's id changes in place.        
        """
        for parameter in F.required_data:
            if parameter not in self.data:
                c = ""
                c += "Instance data does not include required parameter ``%s``."
                c = c % (parameter)
                raise BBExceptions.DefinitionError(c)
        if F.id.bbid:
            self.formula_bbid = F.id.bbid
        else:
            c = ""
            c += "Formula does not have valid bbid; bbid required for use in\n"
            c += "Driver."
            raise BBExceptions.DefinitionError(c)

    def setSignature(self,newSig):
        """


        Driver.setSignature(newSig) -> None


        Method sets self.signature to the specified value. 
        """
        self.signature = newSig

    def setWorkConditions(self,nameCondition,partCondition=None,*tagConditions):
        """


        Driver.setWorkConditions(nameCondition[,partCondition=None
                                          [,*tagConditions]]) -> None


        Method sets workConditions for the instance. ``tagConditions`` collects
        arbitrarily many tags. Method stores each condition as a list. That is,
        self.workConditions["name"] = [nameCondition]. This approach allows for
        use of set operations for checking alignment without breaking
        string-based tags. 

        Setting the value for a given condition to None means all objects match
        that value. If all three conditions are set to None or an empty list,
        the driver will apply to all objects.
        """
        names = []
        parts = []
        tags = []
        if nameCondition:
            names.append(nameCondition.casefold())
        else:
            names.append(nameCondition)
        if partCondition:
            parts.append(partCondition.casefold())
        else:
            parts.append(partCondition)
        for tag in tagConditions:
            if tag:
                tags.append(tag.casefold())
            else:
                tags.append(tag)
        self.workConditions["name"]=names
        self.workConditions["partOf"]=parts
        self.workConditions["allTags"]=tags

    def validate(self):
        """


        Driver.validate() -> bool
        

        Method checks if the instance is properly configured to use formulas.

        Returns False if:
         -- instance points to a formula catalog with 0 keys
         -- instance does not have a formula_bbid
         -- the formula_bbid specified for instance is not in catalog
        True otherwise.
        """
        result = True
        if len(self.FM.local_catalog.by_id) == 0:
            result = False
        if result:
            if not self.formula_bbid:
                result = False
        if result:
            if self.formula_bbid not in self.FM.local_catalog.by_id:
                result = False
        return result
        
    def workOnThis(self,line):
        """


        Driver.workOnThis([line]) -> None


        Method retries Driver's formula from the formula catalog. Method then
        applies the formula to line, with Driver's parentObject, data, and
        signature as context.

        Method is a no-op if instance is not active.
        """
        if self.active:
            if self.canWorkOnThis(line):
                formula = self.FM.local_catalog.issue(self.formula_bbid)
                bu = self.parentObject
                formula.func(line, bu, self.data, self.signature)
                #each funcion is "disposable": delete from memory after single
                #use, get new one next time. 
                del formula
            else:
                c = "Driver cannot work on the specified LineItem."
                raise BBExceptions.BBAnalyticalError(c)
        else:
            pass

#connect Driver class to FormulaManager; now all instances of Driver will be
#able to access FormulaManager.catalog resources
FormulaManager.populate()
Driver.setFormulaManager(FormulaManager)
