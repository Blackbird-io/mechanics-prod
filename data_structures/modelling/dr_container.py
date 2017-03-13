# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2017
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.dr_container
"""

Module defines DriversContainer class, a Components-type container for Driver
objects.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
DriverContainer       class for organizing and storing Drivers
====================  ==========================================================
"""




#imports
import bb_exceptions
from data_structures.modelling.driver import Driver
from data_structures.modelling.container import Container




#globals
#n/a


#classes
class DriverContainer(Container):
    """

    The DriverContainer class provides organization and storage for drivers.
    
    The main directory stores records of known drivers by id.  The by_name
    directory maps driver names to ID's to enable easy lookup by name.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    N/A

    FUNCTIONS:
    get_or_create()       retrieves or creates a driver matching provided info
    ====================  ======================================================
    """

    def __init__(self):
        Container.__init__(self)

    def add(self, obj):
        """


        Container.add() -> None

        --``obj`` is an instance of obj

        Method checks that obj has a valid name and ID and that these
        attributes do not conflict with existing entries before adding the
        new obj.
        """

        # Make sure this obj is valid
        if not obj.id.bbid:
            c = "Cannot add obj that does not have a valid bbid."
            raise bb_exceptions.IDError(c)

        if not obj.name:
            c = "Cannot add obj that does not have a valid name."
            raise bb_exceptions.BBAnalyticalError(c)

        if obj.id.bbid in self.directory:
            c = "Cannot overwrite existing obj. obj with id %s already" \
                " exists in directory." % obj.id.bbid.hex
            raise bb_exceptions.BBAnalyticalError(c)

        if obj.name in self.by_name:
            c = "Cannot overwrite existing obj. obj named %s already" \
                " exists in directory." % obj.name
            raise bb_exceptions.BBAnalyticalError(c)

        self.directory[obj.id.bbid] = obj
        self.by_name[obj.name.casefold()] = obj.id.bbid

    def get_or_create(self, name, data, formula, run_on_past=False):
        """


        DriverContainer.get_or_create() -> Driver

        --``name`` is the name of a Driver
        --``data`` is a dictionary containing data for the Driver
        --``formula`` is a formula object
        --``run_on_past`` is a bool; whether to run the driver on past periods

        Method retrieve a driver by name if it exists, or creates a new driver
        from the provided information.  Raises error if a driver with ``name``
        exists, but has attibutes that don't match provided data and formula.
        """
        driver = self.get_by_name(name)

        if not driver:
            driver = Driver(name)
            driver.configure(data, formula)
            driver.run_on_past = run_on_past
            self.add(driver)  # Adding to Current BU
        else:
            # check data
            data_chk = driver.parameters == data

            # check formula
            form_chk = driver.formula_bbid == formula.id.bbid

            # check run_on_past
            rop_chk = driver.run_on_past == run_on_past

            if not all([data_chk, form_chk, rop_chk]):
                c = "A driver named '%s' exists but has different attributes" \
                    " than those specified as arguments." % name
                raise AssertionError(c)

        return driver
