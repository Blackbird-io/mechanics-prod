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

import bb_exceptions

from data_structures.system.bbid import ID
from data_structures.system.tags import Tags
from content import formula_manager as FormulaManager

from .parameters import Parameters



#constants
#n/a

#classes
class Driver(Tags):
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
    should appear in queue through their position attribute. A driver with a
    position of 10 will run before one with position == 20.

    Drivers do not need to have consecutive positions to run. Queues should
    generally be limited to 5 drivers per line. 

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
    position              int; from 0 to 100
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
    # We will connect the class to the FormulaManager at the bottom of the
    # module. Driver objects will then be able to pull formulas directly
    # from catalog. 

    @classmethod
    def disconnect(cls):
        cls.FM = None
    
    @classmethod
    def setFormulaManager(cls, new_FM):
        cls.FM = new_FM
        
    def __init__(self, signature=None):
        Tags.__init__(self)
        #
        
        
        self.active = True
        self.conversion_table = dict()
        self.data = Parameters()
        self.formula_bbid = None
        self.id = ID()
        #specific uuid assigned when TopicManager configures topic catalog,
        #based on driver's name in topic's namespace id
        
        self.position = 10
        # ``position`` must be an integer value between 0 and 100. used to sort
        # order in which drivers apply to a line.

        self.signature = signature

        self.workConditions = {}
        self.workConditions["name"] = ["FAIL"]
        self.workConditions["partOf"] = ["FAIL"]
        self.workConditions["allTags"] = ["FAIL"]
        #set condition values to a default that must be overwritten to make sure
        #default configuration doesnt apply to every lineItem.

    def __eq__(self, comp, trace=False, tab_width=4):
        """


        Driver.__eq__() -> bool


        Method returns True if instance and comp hash the same, False otherwise.
        """
        result = False
        if hash(self) == hash(comp):
            result = True
        return result

    def __ne__(self, comp, trace=False, tab_width=4):
        """


        Driver.__ne__() -> bool


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
            raise bb_exceptions.IDAssignmentError(c)
        return hash(self.id.bbid)
        #<-------------------------------------------------------------this should really be a hash of the formula,
        # the data, and the work conditions. That means data here should be an immutable mapping. 
    
    def canWorkOnThis(self, targetLineItem):
        """


        Driver.canWorkOnThis() -> bool


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
        
    def configure(self, data, formula, conversion_table=None):
        """


        Driver.configure() -> None


        Method configures instance in proper order: first sets data using
        setData(), then sets formula using setFormula(). The second step
        validates formula against instance data. Use this method to avoid
        errors in topics.         
        """
        if conversion_table is not None:
            self.conversion_table = conversion_table
        
        self._set_parameters(data)
        self.setFormula(formula)
##        self.check_data() #<--------------------------------------------------------------------------------------------think about this
           #the idea is to validate a formula against a particular piece of data
           #should add this to validate? but thats used in a different context
        #<-------------------------------------------------------------------------------WILL HAVE TO REVIEW
        
    def copy(self, enforce_rules=True):
        """


        Driver.copy() -> Driver


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
        result.data = copy.deepcopy(self.data) #<------------------------------------WILL HAVE TO REVIEW
        #<---------------------------------------------------------------------------MAY BE ABLE TO USE SHALLOW COPY
        result.workConditions = copy.deepcopy(self.workConditions)
        return result

##    def setData(self, new_data):
##        """
##
##
##        Driver.setData(new_data) -> None
##
##
##        Method updates instance ``data`` dictionary with a deep copy of
##        new_data.
##        """
##        return self._set_parameters(new_data)

    def _set_parameters(self, new_data):
        new_data = copy.deepcopy(new_data)
        self.data.add(new_data)
        
    def setFormula(self, F):
        """


        Driver.setFormula() -> None


        Sets instance.formula_bbid to that of the argument. Method first checks
        if instance data includes all parameters required by formula.

        #<-----------------------------------------------------------------------------------------------update doc string
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
        if F.id.bbid:
            self.formula_bbid = F.id.bbid
        else:
            c = ""
            c += "Formula does not have valid bbid; bbid required for use in\n"
            c += "Driver."
            raise bb_exceptions.DefinitionError(c)

    def check_data(self, parent=None):
        """
        """
        #<------------------------------------------------------------------------------------------------need doc string
        known_params = self._build_params(parent)
        formula = self.FM.local_catalog.issue(self.formula_bbid)
        
        for parameter in formula.required_data:
            if parameter not in known_params:
                c = ""
                c += "Instance data does not include required parameter ``%s``."
                c = c % (parameter)
                raise bb_exceptions.DefinitionError(c)
        

    def setSignature(self, newSig):
        """


        Driver.setSignature() -> None


        Method sets self.signature to the specified value. 
        """
        self.signature = newSig

    def setWorkConditions(self, nameCondition, partCondition=None, *tagConditions):
        """


        Driver.setWorkConditions() -> None


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
        
    def workOnThis(self, line):
        """


        Driver.workOnThis() -> None


        Method retries Driver's formula from the formula catalog. Method then
        applies the formula to line, with Driver's parentObject, data, and
        signature as context.

        Method is a no-op if instance is not active.
        """
        if self.active:
            if self.canWorkOnThis(line): #<-------------------------------------------------make private
                formula = self.FM.local_catalog.issue(self.formula_bbid) #<-------------------should check to make sure this is just key retrieval
                bu = self.parentObject

                params = self._build_params()
                
                formula.func(line, bu, params, self.signature)
                #each funcion is "disposable": delete from memory after single
                #use, get new one next time. 
                del formula
            else:
                c = "Driver cannot work on the specified LineItem."
                raise bb_exceptions.BBAnalyticalError(c)
        else:
            pass
        #<----------------------------------------------------------------------------------

    def _build_params(self, parent=None):
        """

        -> dict()

        - ``parent`` 
        """
        if parent is None:
            parent = self.parentObject
        period = None
        time_line = None
        
        if parent:
            period = parent.period
        if period:
            time_line = period.parentObject
        
        # Specific parameters trump general ones. Start with time_line, then
        # update for period (more specific) and driver (even more specific).

        params = dict()

        if time_line:
            params.update(time_line.parameters)
        if period:
            params.update(period.parameters)
        
        params.update(self.data)

        converted = self._map_params_to_formula(params)
        params.update(converted)
        # Turn unique shared data into variables formula can understand

        return params

    def _map_params_to_formula(self, params, conversion_table=None):
        """
        -> dict

        return dict with conversion keys and original
        
        """
        
        result = dict()
        
        if conversion_table is None:
            conversion_table = self.conversion_table

        for param_name, var_name in conversion_table.items():
            result[var_name] = params[param_name]
        
        return result

# Connect Driver class to FormulaManager. Now all instances of Driver will be
# able to access FormulaManager.catalog resources.
FormulaManager.populate()
Driver.setFormulaManager(FormulaManager) #<------------------------------------------------------should be private
