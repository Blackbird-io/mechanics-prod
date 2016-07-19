# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.driver
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



 
# Imports
import copy

import bb_exceptions
import bb_settings

from data_structures.serializers.chef import data_management as xl_mgmt
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from data_structures.system.tags_mixin import TagsMixIn
import formula_manager as FormulaManager

from .parameters import Parameters




# Constants
# n/a

# Classes
class Driver(TagsMixIn):
    """

    Drivers apply formulas to business units.

    1) Each Driver applies one and only one formula. 

    A Driver may apply the formula whenever the Driver works on a LineItem
    that satisfies that Driver instance's workConditions. 

    To limit the size of extrapolated models, a Driver instance stores
    only a bbid for its formula, not the formula itself. When the Driver
    has to work, the Driver retrieves the formula from the formula catalog
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
    conversion_table      dict; parameter name : formula argument
    data                  dict; place holder for driver-specific data
    id                    instance of ID
    formula_bbid          bbid for formula that Driver applies
    position              int; from 0 to 100
    relationships         instance of Relationships class
    signature             string; how the driver signs lines it modifies
    workConditions        dict; criteria for objects driver will process

    FUNCTIONS:
    __eq__                True for objects with the same work function              
    __ne__                returns bool negative of __eq__
    __hash__              returns hash of instance bbid, raises error if blank
    copy()                returns a new instance w own objects in key places
    configure()           set data and formula on instance in order
    setSignature()        sets instance signature to object
    setWorkConditions()   sets conditions for suitable objects
    workOnThis()          gets and runs formula with instance data and sig
    validate()            check that driver can perform computations
    ====================  ======================================================
    """
    _FM = None
    # We will connect the class to the FormulaManager at the bottom of the
    # module. Driver objects will then be able to pull formulas directly
    # from catalog. 

    @classmethod
    def _disconnect(cls):
        cls._FM = None
    
    @classmethod
    def _set_formula_manager(cls, new_FM):
        cls._FM = new_FM
        
    def __init__(self, signature=None):
        TagsMixIn.__init__(self)

        self.active = True
        self.conversion_table = dict()
        self.parameters = Parameters()
        self.formula_bbid = None
        self.id = ID()
        self.relationships = Relationships(self)
        # TopicManager will assign a specific uuid to the driver when
        # during topic catalog configuration. Each Driver gets an id within the
        # namespace of its defining topic.
        
        self.position = 10
        # ``position`` must be an integer value between 0 and 100. used to sort
        # order in which drivers apply to a line.

        self.signature = signature

        self.workConditions = {}
        self.workConditions["name"] = ["FAIL"]
        self.workConditions["partOf"] = ["FAIL"]
        self.workConditions["all"] = ["FAIL"]
        # We set condition values to a default that must be overwritten to make
        # sure default configuration doesnt apply to every lineItem.

        self._summary_calculate = False

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
    
        # Ideally, drivers should hash to a combination of the instance formula,
        # params, conversion table, and work conditions. These attributes define
        # what it means for the driver to be the same.
        # 
        # The issue is that params and conversion table are mutable containers.
        # So either have to make them immutable or figure out some other
        # approach. 

    @property
    def summary_calculate(self):
        """
        Default value of summary_calculate is False.  If False, driver will not
        be used in annual summary.  If true, driver will be used in annual
        summary if a matching line exists.
        """
        return self._summary_calculate

    @summary_calculate.setter
    def summary_calculate(self, value):
        self._summary_calculate = value

    def configure(self, data, formula, conversion_table=None):
        """


        Driver.configure() -> None


        Configure instance for use.
        
        Steps:
         -- set instance conversion_table
         -- set instance parameters to data, with overwrite permissions
         -- set formula
        """
        if conversion_table is not None:
            self.conversion_table = conversion_table

        self._set_parameters(data, overwrite=True)
        # Overwrite any existing parameters on configuration. Do this to
        # make sure topics that reconfigure the same driver template can run
        # multiple times. 
        
        self._set_formula(formula)
        
    def copy(self):
        """


        Driver.copy() -> Driver


        Method returns a new Driver object. Result is a shallow copy of instance
        except for the following attributes, which are deep:

        -- parameters
        -- workConditions

        Original object copies tags to result using Tags._copy_tags_to(), so method
        will enforce tag rules when specified.

        Result.relationships.parent points to the same object as original because the
        default shallow copy runs on the ``parentObject`` attribute.

        NOTE: Result points to same object as original on ``id`` and
        ``formula_bbid``. Therefore, the result should continue to point to the
        same formula even if that formula's id changes in place. The result
        should also track any in-place changes to original's id (e.g., change
        in namespace).

        NOTE2: Result points to the original conversion table.
        """
        result = copy.copy(self)
        result.tags = self.tags.copy()
        result.relationships = self.relationships.copy()
        result.parameters = copy.deepcopy(self.parameters)
        result.workConditions = copy.deepcopy(self.workConditions)
        return result
        
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
        self.workConditions["all"]=tags

    def validate(self, check_data=True, parent=None):
        """


        Driver.validate() -> bool
        

        Check if instance is properly configured to do work.

        Returns False iff:
         -- instance points to a formula catalog with 0 keys
         -- instance does not have a formula_bbid
         -- the formula_bbid specified for instance is not in catalog
         -- instance and parent don't supply adequate data (also throws
            exception).        
        """
        result = True
        if len(self._FM.local_catalog.by_id) == 0:
            result = False

        if result:
            if not self.formula_bbid:
                result = False
                
        if result:
            if self.formula_bbid not in self._FM.local_catalog.by_id:
                result = False

        if check_data:
            result = self._check_data(parent) 
        # Always check data, regardless of result. Function will throw
        # exception if the instance lacks required data for the its formula.
        
        return result
        
    def workOnThis(self, line, bu):
        """


        Driver.workOnThis() -> None


        Method retries Driver's formula from the formula catalog. Method then
        applies the formula to line, with Driver's parentObject, data, and
        signature as context.

        Method is a no-op if instance is not active.
        """
        if self.active and not line.hardcoded and not line.has_been_consolidated:
            if self._can_work_on_this(line):
                line.clear()

                formula = self._FM.local_catalog.issue(self.formula_bbid)
                # formula_catalog.issue() only performs dict retrieval and
                # return for key.

                params = self._build_params(parent=bu)

                if not bb_settings.PREP_FOR_EXCEL:

                    formula.func(line, bu, params, self.signature)

                else:
                    output = formula.func(line, bu, params, self.signature)

                    if not output.steps:
                        c = "Formula did not return all required information"
                        c += "\nName: %s" % formula.tags.name
                        c += "\nBBID: %s" % self.formula_bbid
                        c += "\nExcel formula template missing!"

                        raise bb_exceptions.ExcelPrepError(c)

                    data_cluster = self.to_excel()
                    data_cluster.references = output.references
                    data_cluster.name = formula.tags.name
                    data_cluster.comment = output.comment
                    data_cluster.formula = output.steps

                    line.xl.derived.calculations.append(data_cluster)
                
                # Each function is "disposable", so we explicitly delete the
                # pointer after each use.
                del formula

    def to_excel(self):
        """


        Driver.to_excel() -> DriverData

        
        Return a record set with instance parameters and conversion map. 
        """
        result = xl_mgmt.DriverData()
        result.conversion_map = self.conversion_table.copy()

        for param_name, param_value in self.parameters.items():

            row = xl_mgmt.RowData()
            row[xl_mgmt.RowData.field_names.LABELS] = param_name
            row[xl_mgmt.RowData.field_names.VALUES] = param_value

            # UPGRADE / ISSUE: We need to find a way for managing parameters
            # whose values are containers or other mutable structures in Excel.

            result.rows.append(row)

        return result        
    
    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _build_params(self, parent):
        """


        Driver._build_params() -> dict


        Prepare a parameter dictionary for the formula.

        Expects ``parent`` to be a business unit with a defined period pointer.
        
        Method builds its result by collating parameters from the parent,
        parent's time_line and instance. Specific parameters trump general ones.
        Method then converts uniquely named global parameters to standard
        formula arguments using instance.conversion_table. Result includes both
        the original and converted keys.
        """
        period = None
        time_line = None
        
        if parent:
            period = parent.period
            
        if period:
            time_line = period.relationships.parent
        
        # Specific parameters trump general ones. Start with time_line, then
        # update for period (more specific) and driver (even more specific).

        params = dict()

        try:
            params.update(time_line.parameters)
        except AttributeError:
            pass
                                                 
        try:
            params.update(period.parameters)
        except AttributeError:
            pass

        try:
            params.update(parent.parameters)
        except AttributeError:
            pass

        params.update(self.parameters)

        converted = self._map_params_to_formula(params)
        params.update(converted)
        # Turn unique shared data into common variables that the formula can
        # understand. So a key like "lowest maintenance bid" becomes
        # "base annual expense".

        return params

    def _can_work_on_this(self, line):
        """


        Driver._can_work_on_this() -> bool


        This method checks whether the line satisfies workConditions.
        If the line satisfies each of the workConditions specified for
        the instance, the method returns True. Otherwise, the method returns
        False.

        To satisfy the allTags condition, an object must carry each tag in
        instance.workConditions["all"] (ie, instance.wC[allTags] must be
        a subset of target.tags.all).

        NOTE: driver.workConditions keys may include None as values to indicate
        absence of a constraint. Accordingly, match is evaluated against
        candidate attributes plus a None element.

        A workCondition with a value equal to None or an empty list will be
        satisfied for all lineItems.
        """

        # must be careful not to split strings (names) into letters with set()
        if self.workConditions["name"]:
            if not set(self.workConditions["name"]).issubset([line.name] + [None]):
                return False

        if self.workConditions["partOf"]:
            try:
                part_of = set([line.relationships.parent.name]) | {None}
            except AttributeError:
                part_of = {None}

            if not set(self.workConditions["partOf"]).issubset(part_of):
                return False

        if self.workConditions["all"]:
            all_tags = line.tags.all | set([line.name]) | {None}

            if not set(self.workConditions["all"]).issubset(all_tags):
                return False

        return True

    def _check_data(self, parent=None):
        """


        Driver._check_data() -> bool


        Check if instance and parent specify all required data for formula.
        Throw DefinitionError if that's not the case.
        """
        result = False
        
        known_params = self._build_params(parent)
        formula = self._FM.local_catalog.issue(self.formula_bbid)
        
        for parameter in formula.required_data:
            if parameter not in known_params:
                c = ""
                c += "Instance data does not include required parameter ``%s``."
                c = c % (parameter)
                raise bb_exceptions.DefinitionError(c)
                break
        else:
            result = True

        return result
    
    def _map_params_to_formula(self, params, conversion_table=None):
        """


        Driver._map_params_to_formula() -> dict


        Return a dictionary that maps values from ``params`` to keys in the
        conversion table.         
        """
        result = dict()
        
        if conversion_table is None:
            conversion_table = self.conversion_table

        for param_name, var_name in conversion_table.items():
            result[var_name] = params[param_name]
        
        return result

    def _set_formula(self, F):
        """


        Driver._set_formula() -> None


        Set instance.formula_bbid to that of the argument.
        """
        if F.id.bbid:
            self.formula_bbid = F.id.bbid
        else:
            c = ""
            c += "Formula does not have valid bbid; bbid required for use in\n"
            c += "Driver."
            raise bb_exceptions.DefinitionError(c)

    def _set_parameters(self, new_data, overwrite=False):
        """


        Driver._set_parameters() -> None


        Add new_data to instance.parameters. 
        """
        new_data = copy.deepcopy(new_data)
        self.parameters.add(new_data, overwrite)

# Connect Driver class to FormulaManager. Now all instances of Driver will be
# able to access FormulaManager.catalog resources.
FormulaManager.populate()
Driver._set_formula_manager(FormulaManager)
