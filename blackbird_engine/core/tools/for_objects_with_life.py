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
====================         ===================================================
Attribute                    Description
====================         ===================================================

DATA:
n/a

FUNCTIONS:
make_units_linear()          create an exact number of units linearly over time
make_units_growth_numbered() create an exact number of units w/ geometric growth
make_units_growth_rate()     create units w/ geometric growth, given a rate
make_units_closed_linear()   create units that have opened and closed uniformly
get_units_linear()           get exact num of existing units uniformly over time

CLASSES:
n/a
====================         ===================================================
"""




#imports
import BBExceptions
import math
from datetime import date
from datetime import timedelta




#functions
def make_units_linear(start_dt, end_dt, number, template):
    """


    make_units_linear() -> List


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


def make_units_growth_numbered(start_dt, end_dt, number, template, start_num):
    """


    make_units_growth_numbered() -> None


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
    time_diff_years = time_diff.days / 365
    """
    Let S = start_num
    Let K = count or number of units added
    Let r = rate
    Let t = timedelta (from start_dt)

    S * e^(rt) - S = K
    S *( (e^(rt) - 1) = K
    e^(rt) = K/S + 1

    t = (1/r) * ln( K/S + 1 )

    So if we want to know the time that 1st unit opens, K = 1,
    We can just solve for t by plugging in K:

    t1 = (1/r) * ln( 1/S + 1 )      1st Unit Opens
    t2 = (1/r) * ln( 2/S + 1 )      2nd Unit Opens
    t3 = (1/r) * ln( 3/S + 1 )      3rd Unit Opens
    ...

    birth_dates = [t1 + start_dt, t2 + start_dt, t3 + start_dt, ...]

    If we know t, S, and K, we can also derive an equation for rate as well

    t = (1/r) * ln( K/S + 1 )    ***Equation (A)***

    r = (1/t) * ln( K/S + 1 )    ***Equation (B)***

    """
    # 1st figure out annual continuous rate growth rate:
    rate = (1/time_diff_years) * math.log(number/start_num + 1)  # Equation A
    print("Rate:", rate)

    birth_dates = []
    for K in range(number):
        t = (1/rate) * math.log((K+1)/start_num + 1)  # Equation B
        t_timedelta = timedelta(t * 365)
        birth_dates.append(t_timedelta + start_dt)

    unit_count = 0
    for birthday in birth_dates:
        copy = template.copy()
        unit_count += 1
        copy.name += str(unit_count)
        copy.life.configure_events(birthday)
        # Sets events: conception, birth, death, maturity, old_age
        population.append(copy)

    return population


def make_units_growth_rate(start_dt, end_dt, rate, template, start_num):
    """


    make_units_growth_rate() -> list()


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
    time_diff_years = time_diff.days / 365
    """
    Let S = start_num
    Let K = count or number of units to be created
    Let r = rate
    Let t = timedelta (from start_dt)

    S * e^(rt) - S = K
    S *( (e^(rt) - 1) = K
    e^(rt) = K/S + 1

    t = (1/r) * ln( K/S + 1 )

    So if we want to know the time that 1st unit opens, K = 1,
    We can just solve for t by plugging in K:

    t1 = (1/r) * ln( 1/S + 1 )      1st Unit Opens
    t2 = (1/r) * ln( 2/S + 1 )      2nd Unit Opens
    t3 = (1/r) * ln( 3/S + 1 )      3rd Unit Opens
    ...

    birth_dates = [t1 + start_dt, t2 + start_dt, t3 + start_dt, ...]

    If we know t, S, and K, we can also derive an equation for rate as well

    t = (1/r) * ln( K/S + 1 )    ***Equation (A)***

    r = (1/t) * ln( K/S + 1 )    ***Equation (B)***
    """
    # 1st figure out total number of units to be created :
    number = start_num * math.exp(rate * time_diff_years) - start_num
    number = math.floor(number)

    birth_dates = []
    for K in range(number):
        t = (1/rate) * math.log((K+1)/start_num + 1)  # Equation B
        t_timedelta = timedelta(t * 365)
        birth_dates.append(t_timedelta + start_dt)

    unit_count = 0
    for birthday in birth_dates:
        copy = template.copy()
        unit_count += 1
        copy.name += str(unit_count)
        copy.life.configure_events(birthday)
        # Sets events: conception, birth, death, maturity, old_age
        population.append(copy)

    return population



def make_units_closed_linear(start_dt, end_dt, number, template, birth_dt=None):
    """


    make_units_closed_linear() -> List


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


def get_units_linear(number, container):
    """


    get_units_linear() -> list


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




