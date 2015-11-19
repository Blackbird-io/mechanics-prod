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
import BBExceptions
import math
from datetime import date
from datetime import timedelta




#functions
def make_linear_pop(start_dt, end_dt, number, template):
    """


    add_bu_linear() -> List


    Returns a list of objects with uniform birth dates

    start_dt            -- datetime.date
    end_dt              -- datetime.date
    number              -- integer, number of templates to be created
    template            -- object with Life attribute, ie a BusinessUnit

    """
    time_diff = end_dt - start_dt  # timedelta object
    time_interval = time_diff / number
    birth_index = start_dt + time_interval/2  # Start in middle of time period

    population = []
    for i in range(number):
        copy = template.copy()
        copy.name += " " + str(i+1)
        copy.life.configure_events(birth_index)
        # Sets events: conception, birth, death, maturity, old_age
        birth_index += time_interval
        population.append()

    return population


def make_growing_pop_fixed_num(start_dt, end_dt, number, template, start_num):
    """


    add_bu_growth_num() -> None


    Returns list of a fixed number of objects with constant geometric growth
    rate over time.

    start_dt            -- datetime.date
    end_dt              -- datetime.date
    number              -- integer, number of templates to be created
    template            -- object with Life attribute, ie a BusinessUnit
    start_num           -- int, number of starting BUs of this same type

    The total number of objects created must be known, so this function is
    useful for populating historical time periods and near term forecasts.
    Generally for creating less than 5 units it is better to use use
    make_linear_pop instead.
    """
    population = []
    time_diff = end_dt - start_dt  # timedelta object
    # Figure out implied yearly growth rate
    end_num = number + start_num
    growth = math.log(end_num / start_num) / time_diff.days
    count = start_num  # total number of bu of this type at any given time

    first_open = end_dt  # to be changed later in the loop to 1st opening date
    adds = 0.5  # adds 1st bu in the middle of period, instead of at start date

    # Following code increments adds by the growth in each period. Each time
    # adds is greater than 1, we create a unit and append it to population
    growth_multiplier = (math.exp(growth) - 1)
    for t in range(time_diff.days):
        base = count + adds - 0.5  # subtracting original 0.5 period adjustment
        per_period_unit_change = base * growth_multiplier
        adds += per_period_unit_change
        # adds is number of units to add per day
        while adds >= 1:
            adds -= 1
            count += 1
            copy = template.copy()
            copy.name += " " + str(count)
            copy.life.configure_events(start_dt + timedelta(t))
            # Sets events: conception, birth, death, maturity, old_age
            first_open = min(end_dt, start_dt + timedelta(t))
            population.append(copy)

    # if starting num = 1 or 2, this approximation will under fill the number of
    # units created because of rounding. To fix this we add the remainder of the
    # units in the beginning.
    if number + start_num > count:
        extras = number + start_num - count
        pop_extra = make_linear_pop(start_dt, first_open, extras, template)
        # Insert pop_extra at the beginning of population
        population = pop_extra + population

    return population


def make_growing_pop_fixed_rate(start_dt, end_dt, rate, template, start_num):
    """


    make_growing_pop_fixed_rate() -> list()


    Makes units over time with constant geometric growth given a fixed rate.

    start_dt            -- datetime.date
    end_dt              -- datetime.date
    rate                -- float, annual growth rate relative to % of start_num
    template            -- object with Life attribute, ie a BusinessUnit
    start_num           -- int, number of starting BUs of this same type

    Note that for long time periods, the number of units created is very
    sensitive to rate and start_num. Start_num may be any reference point,
        IE: template = Mules, start_num = average(Donkeys, Horses)
    This function is better suited towards creating future business units than
    back-filling historical openings since we don't know the exact number of
    units that will be created.
    """
    population = []
    time_diff = end_dt - start_dt  # timedelta object
    # Figure out implied yearly growth rate
    growth = math.log(1 + rate) / 365  # Convert to daily continuous growth rate
    count = start_num  # total number of bu of this type at any given time

    """
    #####################################################
    period_length = 30
    periods = (end_dt - start_dt)/ period_length
    ln_one_plus_rate = math.log(end_dt/start_dt) / periods
    one_plus_rate = math.exp(ln_one_plus_rate)

    remaining = ending - starting

    for i in range(periods):
        remaining = ending - starting
        new = base * one_plus_rate
        new = math.ceil(new)
        # Always an integer, get there faster, we are
        # approximating anyways
        new = min(new, remaining)
        for j in range(new):
            # copy obj
            # set life
            # set name (may be seed + str(period) + j?)
            population.append(new_obj)
            starting += new
            if starting == new:
            break
            # once we've rounded up, stop work
    #####################################################
    """

    first_open = end_dt
    adds = 0.5  # adds 1st bu in the middle of period, instead of at start date
    growth_multiplier = (math.exp(growth) - 1)
    # For each period, adds is incremented by the amount of growth
    for t in range(time_diff.days):
        base = count + adds - 0.5  # subtracting original 0.5 period adjustment
        per_period_unit_change = base * growth_multiplier
        adds += per_period_unit_change
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


def make_closed_pop_linear(start_dt, end_dt, number, template, birth_dt=None):
    """


    make_closed_pop_linear() -> List


    Creates a fixed number of units and then closes them linearly over the
    dates given.

    start_dt            -- datetime.date
    end_dt              -- datetime.date
    number              -- integer, number of templates to be created
    template            -- object with Life attribute, ie a BusinessUnit
    birth_dt            -- datetime.date, birth date returned units

    All units are assumed to have the same birth date for simplicity.
    Unless specified, birth_dt = start_dt
    """
    population = []

    if not birth_dt:
        birth_dt = start_dt
    elif birth_dt > start_dt:
        c = "Warning Birth Date > Start Date!"
        raise BBExceptions.BBAnalyticalError(c)

    time_diff = end_dt - start_dt  # timedelta object
    time_interval = time_diff / number
    date_index = start_dt + time_interval/2  # Start in middle of time period

    for i in range(number):
        copy = template.copy()
        copy.name = template.name + " " + (i+1)
        copy.life.configure_events(birth_dt)
        # Sets events: conception, birth, death, maturity, old_age
        copy.kill(date_index)
        date_index += time_interval
        population.append(copy)

    return population


def get_pop_linear(number, container):
    """


    get_pop_linear() -> list


    Returns a list with a fixed number of existing units, which are evenly
    distributed by age ranking. List is ordered by birth date.

    number              -- integer, number of objects to be returned
    container           -- iterable, containing objects with life attr

    User should decide what goes into container. Can include dead units, alive
    units, or gestating + alive units. User should also decide what date filters
    to use for the container objects.
    """
    # Error Checking
    if number > len(container):
        print('Error: Number > Container Length')
        raise BBExceptions.BBAnalyticalError

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




