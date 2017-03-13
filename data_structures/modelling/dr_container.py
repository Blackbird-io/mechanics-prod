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




#globals
#n/a


#classes
class DriverContainer():
    """

    The DriverContainer class provides organization and storage for drivers.
    
    The main directory stores records of known drivers by id.  The by_name
    directory maps driver names to ID's to enable easy lookup by name.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    directory             dict; holds drivers keyed by BBID
    by_name               dict; maps driver name to BBID

    FUNCTIONS:
    add()                 adds a new driver
    copy()                returns a deep copy of self and all keys and drivers
    get()                 retrieves a driver by id
    get_or_create()       retrieves or creates a driver matching provided info
    get_by_name()         retrieves a driver by name
    remove()              removes a driver by id
    ====================  ======================================================
    """

    def __init__(self):
        self.directory = dict()
        self.by_name = dict()

    def add(self, driver):
        """


        DriverContainer.add() -> None

        --``driver`` is an instance of Driver

        Method checks that driver has a valid name and ID and that these
        attributes do not conflict with existing entries before adding the
        new driver.
        """

        # Make sure this driver is valid
        if not driver.id.bbid:
            c = "Cannot add driver that does not have a valid bbid."
            raise bb_exceptions.IDError(c)

        if not driver.name:
            c = "Cannot add driver that does not have a valid name."
            raise bb_exceptions.BBAnalyticalError(c)

        if driver.id.bbid in self.directory:
            c = "Cannot overwrite existing driver. Driver with id %s already" \
                " exists in directory." % driver.id.bbid.hex
            raise bb_exceptions.BBAnalyticalError(c)

        if driver.name in self.by_name:
            c = "Cannot overwrite existing driver. Driver named %s already" \
                " exists in directory." % driver.name
            raise bb_exceptions.BBAnalyticalError(c)
        
        self.directory[driver.id.bbid] = driver
        self.by_name[driver.name.casefold()] = driver.id.bbid

    def copy(self):
        """


        DriverContainer.copy() -> DriverContainer

        Method returns a new DriverContainer instance. The items in the copy
        instance itself (tag : set of bbids) are identical to that of the
        original. The drivers in the copy directory are copies of the drivers
        in the original directory.
        """

        result = DriverContainer()

        for driver in self.directory.values():
            result.add_item(driver.copy())

        return result

    def get(self, bbid):
        """


        DriverContainer.get() -> Driver or None

        --``bbid`` is a UUID corresponding to a Driver

        Method returns driver with provided BBID or None.
        """
        result = None
        if bbid:
            result = self.directory.get(bbid, None)

        return result
    
    def get_by_name(self, name):
        """


        DriverContainer.get_by_name() -> Driver or None

        --``name`` is the name of a Driver

        Method uses provided name to search for and return a Driver or None.
        """
        result = None
        bbid = self.by_name.get(name, None)
        if bbid:
            result = self.directory.get(bbid, None)
        return result

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

    def remove(self, bbid):
        """


        DriverContainer.remove() -> None

        Method removes driver with given BBID.
        """
        dr = self.directory.pop(id, None)
        if dr:
            self.by_name.pop(dr.name)
