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
from data_structures.system.tags import Tags
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
    run_on_past           bool; default is False, whether to run driver in past
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

    def __init__(self, name=None):
        TagsMixIn.__init__(self, name=name)

        self.conversion_table = dict()
        self.formula_bbid = None
        self.id = ID()
        self.parameters = Parameters()
        self.run_on_past = False
        # OBSOLETE
        self.workConditions = dict()
        self.active = True

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

    @property
    def signature(self):
        return self.name

    @classmethod
    def from_database(cls, portal_data):
        new = cls()
        new.tags = Tags.from_database(portal_data.get('tags'))
        new.conversion_table = portal_data.get('conversion_table')
        new.formula_bbid = ID.from_database(portal_data.get('formula_bbid')).bbid
        new.parameters = Parameters.from_database(portal_data.get('parameters'),
                                                target='parameters')
        new.run_on_past = portal_data.get('run_on_past', False)

        formula = cls._FM.local_catalog.issue(new.formula_bbid)
        new.id.set_namespace(formula.id.namespace)
        new.id.assign(new.name or formula.tags.name)

        return new

    def to_database(self):
        data = dict()
        data['tags'] = self.tags.to_database()
        data['conversion_table'] = self.conversion_table
        data['formula_bbid'] = self.formula_bbid.hex
        data['parameters'] = list(self.parameters.to_database(
            target='parameters'))
        data['run_on_past'] = self.run_on_past

        return data

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

        # get namespace for driver
        base = self.name or formula.tags.name
        self.id.set_namespace(formula.id.namespace)
        self.id.assign(seed=base)

    def copy(self):
        """


        Driver.copy() -> Driver


        Method returns a new Driver object. Result is a shallow copy of instance
        except for the following attributes, which are deep:

        -- parameters
        -- workConditions

        Original object copies tags to result using Tags._copy_tags_to(), so method
        will enforce tag rules when specified.

        NOTE: Result points to same object as original on ``id`` and
        ``formula_bbid``. Therefore, the result should continue to point to the
        same formula even if that formula's id changes in place. The result
        should also track any in-place changes to original's id (e.g., change
        in namespace).

        NOTE2: Result points to the original conversion table.
        """
        result = copy.copy(self)
        result.tags = self.tags.copy()
        result.parameters = copy.deepcopy(self.parameters)
        result.formula_bbid = copy.copy(self.formula_bbid)

        return result

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

    def workOnThis(self, line, bu, period=None):
        """


        Driver.workOnThis() -> None


        Method retries Driver's formula from the formula catalog. Method then
        applies the formula to line, with Driver's parentObject, data, and
        signature as context.

        Method is a no-op if instance is not active.
        """

        tl = period.relationships.parent
        if tl is tl.model.time_line:
            if period is tl.current_period.past:
                if not self.run_on_past:
                    return

        if all((
            not line.hardcoded,
            not line.has_been_consolidated,
            not (line.sum_details and line._details)
        )):
            line.clear(recur=False)

            formula = self._FM.local_catalog.issue(self.formula_bbid)
            # formula_catalog.issue() only performs dict retrieval and
            # return for key.

            params = self._build_params(parent=bu, period=period)

            if not bb_settings.PREP_FOR_EXCEL:
                formula.func(line, bu, params, self.signature)
            else:
                output = formula.func(line, bu, params, self.signature)

                if not output.steps:
                    c = (
                        "Formula did not return all required information\n"
                        "Name: {name}\n"
                        "BBID: {bbid}\n"
                        "Excel formula template missing!"
                    ).format(
                        name=formula.tags.name,
                        bbid=self.formula_bbid,
                    )
                    raise bb_exceptions.ExcelPrepError(c)

                data_cluster = self.to_excel()
                data_cluster.references = output.references
                data_cluster.name = formula.tags.name
                data_cluster.comment = output.comment
                data_cluster.formula = output.steps

                line.xl_data.add_derived_calculation(data_cluster)

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

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _build_params(self, parent, period=None):
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
        if not period:
            period = parent.get_current_period()
        params = parent.get_parameters(period)
        params.update(self.parameters)

        converted = self._map_params_to_formula(params)
        params.update(converted)
        # Turn unique shared data into common variables that the formula can
        # understand. So a key like "lowest maintenance bid" becomes
        # "base annual expense".

        # extra info needed by formulas
        params['period'] = period

        return params

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

    def setWorkConditions(self, *kwargs):
        # OBSOLETE
        pass

# Connect Driver class to FormulaManager. Now all instances of Driver will be
# able to access FormulaManager.catalog resources.
FormulaManager.populate()
Driver._set_formula_manager(FormulaManager)
