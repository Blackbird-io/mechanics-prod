# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2015
# NOT TO BE CIRCULATED OR REPRODUCED
# WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

# Blackbird Engine
# Module: tools.for_objects_with_life

"""

Module includes convenience functions that return a population of objects
All objects must have a Life attribute
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
add_bu_linear()       create an exact number of BUs linearly over time
add_bu_growth_num()   create an exact number of BUs with geometric growth
add_bu_growth_rate()  create BUs with geometric growth given a growth rate
add_prev_closings()   create BUs that have opened and closed in the past
close_bu_linear()     close an exact number existing BUs linearly over time

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import math
from datetime import date
from datetime import timedelta




#functions
def make_linear_pop(start_dt, end_dt, number, template):
    """


    add_bu_linear() -> List


    Returns a list of objects with uniform birth dates

    start_dt, end_dt    -- datetime.date
    number              -- integer, number of templates to be created
    template            -- object with Life attribute, ie a BusinessUnit

    """
    time_diff = end_dt - start_dt  # timedelta object
    time_interval = time_diff / number
    birth_index = start_dt + time_interval/2  # Start in middle of time period

    population = []
    for i in range(number):
        copy = template.copy()
        copy.life.configure_events(birth_index)
        # Sets events: conception, birth, death, maturity, old_age
        birth_index += time_interval
        copy.name = template.type
        population.append()

    return population


def make_growing_pop_fixed_num(start_dt, end_dt, number, template, start_num):
    """


    add_bu_growth_num() -> None


    Returns list of a fixed number of objects with constant geometric growth
    rate over time.

    start_dt, end_dt    -- datetime.date
    number              -- integer, number of templates to be created
    template            -- object with Life attribute, ie a BusinessUnit
    start_num           -- int, number of starting BUs of this same type

    The total number of objects created must be known.
    Note that it is better NOT to use this method if the number of existing
    BUs are low (<3). Please use add_bu_linear instead.
    """
    population = []
    time_diff = end_dt - start_dt  # timedelta object
    # Figure out implied yearly growth rate
    end_num = number + start_num
    growth = math.log(end_num / start_num) / time_diff.days
    count = start_num  # total number of bu of this type at any given time

    first_open = end_dt
    adds = 0.5  # adds 1st bu in the middle of period, instead of at start date

    for t in range(time_diff.days):
        adds += (count + adds - 0.5) * (math.exp(growth) - 1)
        # adds is number of units to add per day
        while adds >= 1:
            adds -= 1
            count += 1
            copy = template.copy()
            copy.name += count
            copy.life.configure_events(start_dt + timedelta(t))
            # Sets events: conception, birth, death, maturity, old_age
            first_open = min(end_dt, start_dt + timedelta(t))
            population.append(copy)

    # if starting num = 1 or 2, this approximation will under fill the number of
    # business units created because of severe rounding. To fix this we add
    # the remainder of the business units in the beginning.
    # Note that it is better not to use this method of the number of existing
    # BUs are low. Use add_bu_linear instead for that time period
    print("Total BU Created", count - start_num)

    if number + start_num > count:
        extras = number + start_num - count
        pop_extra = make_linear_pop(start_dt, first_open, extras, template)
        # Insert pop_extra at the beginning of population
        population = pop_extra + population

    return population


def make_growing_pop_fixed_rate(start_dt, end_dt, rate, template, start_num):
    """


    make_growing_pop_fixed_rate() -> list()


    start_dt, end_dt        -- datetime.date
    number                  -- integer, number of templates to be created
    template                -- object with Life attribute, ie a BusinessUnit
    start_num to be an int, number of starting BUs of this same type

    Function creates business units with variable birth dates over time that
    reflects constant growth rate. Adds these BU to the components of parent.
    Function requires known growth rate and starting number of units.
    However, start_num may be any reference point,
        IE template = Mules, start_num = average(Donkeys, Horses)
    This function is better suited towards creating future business units than
    back-filling historical openings.
    """
    population = []
    time_diff = end_dt - start_dt  # timedelta object
    # Figure out implied yearly growth rate
    growth = math.log(1 + rate) / 365  # Convert to daily continuous growth rate
    count = start_num  # total number of bu of this type at any given time

    first_open = end_dt
    adds = 0.5  # adds 1st bu in the middle of period, instead of at start date
    for t in range(time_diff.days):
        adds += (count + adds -0.5) * (math.exp(growth) - 1)
        # adds is number of units to add per day
        while adds >= 1:
            adds += -1
            count += 1
            copy = template.copy()
            copy.name = str(template.type) + str(count)
            copy.life.configure_events(start_dt + timedelta(t))
            # Sets events: conception, birth, death, maturity, old_age
            population.append(copy)

    print("Total Units Created",count - start_num)


def add_prev_closings(start_dt, end_dt, number, template, parent):
    """


    add_prev_closings() -> None


    start_dt, end_dt        -- datetime.date
    number                  -- integer, number of templates to be created
    template                -- object with Life attribute, ie a BusinessUnit
    start_num to be an int, number of starting BUs of this same type

    Expects start_dt, end_dt to be datetime.date
    Expects number to be integer for number of business units to be added
    Expects template to be a BusinessUnit obj template to be copied and created
    Expects parent to be a BusinessUnit obj, whose components we are adding

    Function adds a number of business units and then closes them linearly
    over the dates given. Adds these dead BU to the components of parent
    All BU are assumed to have the same birth date as parent for simplicity
    """
    population = []
    time_diff = end_dt - start_dt  # timedelta object
    time_interval = time_diff / number
    date_index = start_dt + time_interval/2  # Start in middle of time period
    parent_dob = parent.life.events['birth']

    for i in range(number):
        copy = template.copy()
        #est_birth = max(date_index - timedelta(copy.life.span or 0), parent_dob)
        est_birth = parent_dob
        # Makes sure birth date is not before parents birth
        copy.life.configure_events(est_birth)
        # Sets events: conception, birth, death, maturity, old_age
        copy.kill(date_index)
        copy.tag("closed")
        date_index += time_interval
        copy.name = str(copy.type) + " closed " + str(i+1)
        population.append(copy)

    return population


def get_pop_linear(number, container):
    """


    get_pop_linear() -> list


    Returns a list with a fixed number of existing units, which are evenly
    distributed by age ranking. List is ordered by birth date.

    start_dt, end_dt        -- datetime.date
    number                  -- integer, number of objects to be returned
    container               -- iterable, containing objects with life attr

    User should decide what goes into container. Can include dead units, alive
    units, or gestating + alive units. User should also decide what date filters
    to use for the container objects.
    """
    # Error Checking
    if number > len(container):
        print('Error: Number > Container Length')
        raise IndexError

    # Populate master_list, a sorted list of container objects by birth date
    master_list = list()
    if type(container) == dict():
        master_list = list(container.values())
    else:  # list, set both work here
        master_list = container

    master_list.sort(key=lambda x: x.life.events['birth'])

    len_master = len(master_list)
    index_interval = len_master/number
    # Don't choose are not end units, unless you have to because of number
    index = 0 + math.floor(index_interval/2)

    population = []

    if number == len_master:
        population = master_list
        # Save all the time if we want all of the units anyways
    elif number < len_master/2:
        # Append units from master list if choosing less than 1/2 of them
        for i in range(number):
            target_bu = master_list[index]
            population.append(target_bu)
            units_needed = number - i - 1
            if units_needed:
                len_remaining = len_master - index - index_interval/2
                # index_interval/2 also leaves a buffer at the end if necessary
                index_interval = len_remaining/units_needed
                index += round(index_interval)
    else:
        # Remove units from master list if choosing more than 1/2 of them
        for i in range(len_master-number):
            target_bu = master_list[index]
            master_list.remove(target_bu)
            units_needed = number - i - 1
            if units_needed:
                len_remaining = len_master - index - index_interval/2
                # index_interval/2 also leaves a buffer at the end if necessary
                index_interval = len_remaining/units_needed
                index += round(index_interval)
        population = master_list

    return population


