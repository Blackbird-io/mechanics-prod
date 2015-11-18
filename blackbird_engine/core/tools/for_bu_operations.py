# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2015
# NOT TO BE CIRCULATED OR REPRODUCED
# WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

# Blackbird Engine
# Module: tools.for_bu_operations

"""

Module includes convenience functions for creating and killing business units
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

#n/a




#globals
#n/a

#functions
def add_bu_linear(start_date, end_date, number, bu_copy, parent, start_num):
    """


    add_bu_linear() -> None


    Expects start_date, end_date to be datetime.date
    Expects number to be integer for number of business units to be added
    Expects bu_copy to be a BusinessUnit obj template to be copied and created
    Expects parent to be a BusinessUnit obj, whose components we are adding
    Expects start_num to be an int, number of starting BUs of this same type

    Function makes a number of business units with linear birth date over time
    Adds these BU to the components of parent
    """
    time_diff = end_date - start_date  # timedelta object
    time_interval = time_diff / number
    date_index = start_date + time_interval/2  # Start in middle of time period
    for i in range(number):
        bu = bu_copy.copy()
        bu.life.configure_events(date_index)
        # Sets events: conception, birth, death, maturity, old_age
        date_index += time_interval
        bu.name = str(bu.type) + str(start_num + i)
        parent.add_component(bu)


def add_bu_growth_num(start_date, end_date, number, bu_copy, parent, start_num):
    """


    add_bu_growth_num() -> None


    Expects start_date, end_date to be datetime.date
    Expects number to be integer for number of business units to be added
    Expects bu_copy to be a BusinessUnit obj template to be copied and created
    Expects parent to be a BusinessUnit obj, whose components we are adding
    Expects start_num to be an int, number of starting BUs of this same type

    Function makes a number of business units with birth date over time that
    reflects constant growth rate. Adds these BU to the components of parent.
    The total number of business units created must be known.
    Note that it is better NOT to use this method if the number of existing
    BUs are low (<3). Please use add_bu_linear instead.
    """
    time_diff = end_date - start_date  # timedelta object
    # Figure out implied yearly growth rate
    end_num = number + start_num
    growth = math.log(end_num / start_num) / time_diff.days
    count = start_num  # total number of bu of this type at any given time

    first_open = end_date
    adds = 0.5  # adds 1st bu in the middle of period, instead of at start date
    for t in range(time_diff.days):
        adds += (count + adds - 0.5) * (math.exp(growth) - 1)
        # adds is number of units to add per day
        while adds >= 1:
            adds += -1
            count += 1
            bu = bu_copy.copy()
            bu.name = str(bu.type) + str(count)
            bu.life.configure_events(start_date + timedelta(t))
            # Sets events: conception, birth, death, maturity, old_age
            first_open = min(end_date, start_date + timedelta(t))
            parent.add_component(bu)

    # if starting num = 1 or 2, this approximation will under fill the number of
    # business units created because of severe rounding. To fix this we add
    # the remainder of the business units in the beginning.
    # Note that it is better not to use this method of the number of existing
    # BUs are low. Use add_bu_linear instead for that time period
    print("Total BU Created",count - start_num)

    if number + start_num > count:
        extras = number + start_num - count
        add_bu_linear(start_date, first_open, extras, bu_copy, parent, 0)
        # renumber the BU.name
        bu_list = list(parent.components.values())
        bu_list.sort(key = lambda x: x.life.events['birth'])
        for i in range(len(bu_list)):
            bu_list[i].name = str(bu_list[i].type) + " " + str(start_num + i+1)


def add_bu_growth_rate(start_date, end_date, rate, bu_copy, parent, start_num):
    """


    add_bu_growth_rate() -> None


    Expects start_date, end_date to be datetime.date
    Expects rate to be float, annually compounded yearly growth rate
    Expects bu_copy to be a BusinessUnit obj template to be copied and created
    Expects parent to be a BusinessUnit obj, whose components we are adding
    Expects start_num to be an int, number of starting BUs of this same type

    Function creates business units with variable birth dates over time that
    reflects constant growth rate. Adds these BU to the components of parent.
    Function requires known growth rate and starting number of units.
    However, start_num may be any reference point,
        IE bu_copy = Mules, start_num = average(Donkeys, Horses)
    This function is better suited towards creating future business units than
    back-filling historical openings.
    """
    time_diff = end_date - start_date  # timedelta object
    # Figure out implied yearly growth rate
    growth = math.log(1 + rate) / 365  # Convert to daily continuous growth rate
    count = start_num  # total number of bu of this type at any given time

    first_open = end_date
    adds = 0.5  # adds 1st bu in the middle of period, instead of at start date
    for t in range(time_diff.days):
        adds += (count + adds -0.5) * (math.exp(growth) - 1)
        # adds is number of units to add per day
        while adds >= 1:
            adds += -1
            count += 1
            bu = bu_copy.copy()
            bu.name = str(bu.type) + str(count)
            bu.life.configure_events(start_date + timedelta(t))
            # Sets events: conception, birth, death, maturity, old_age
            parent.add_component(bu)

    print("Total BU Created",count - start_num)


def add_prev_closings(start_date, end_date, number, bu_copy, parent):
    """


    add_prev_closings() -> None


    Expects start_date, end_date to be datetime.date
    Expects number to be integer for number of business units to be added
    Expects bu_copy to be a BusinessUnit obj template to be copied and created
    Expects parent to be a BusinessUnit obj, whose components we are adding

    Function adds a number of business units and then closes them linearly
    over the dates given. Adds these dead BU to the components of parent
    All BU are assumed to have the same birth date as parent for simplicity
    """
    time_diff = end_date - start_date  # timedelta object
    time_interval = time_diff / number
    date_index = start_date + time_interval/2  # Start in middle of time period
    parent_dob = parent.life.events['birth']
    for i in range(number):
        bu = bu_copy.copy()
        #est_birth = max(date_index - timedelta(bu.life.span or 0), parent_dob)
        est_birth = parent_dob
        # Makes sure birth date is not before parents birth
        bu.life.configure_events(est_birth)
        # Sets events: conception, birth, death, maturity, old_age
        bu.kill(date_index)
        bu.tag("closed")
        date_index += time_interval
        bu.name = str(bu.type) + " closed " + str(i+1)
        parent.add_component(bu)


def close_bu_linear(start_date, end_date, number, bu_copy, parent):
    """


    close_bu_linear() -> None


    Expects start_date, end_date to be datetime.date
    Expects number to be integer for number of business units to be killed
    Expects bu_copy to be a BusinessUnit obj template to be killed,
    Expects parent to be a BusinessUnit obj, whose components we are adding

    Function closes a fixed number of units over time from the parent's
    components and matching the same type as bu_copy
    """
    time_diff = end_date - start_date  # timedelta object
    time_interval = time_diff / number
    date_index = start_date + time_interval/2  # Start in middle of time period
    living_bu_dict = parent.components.get_living()
    living_bu_set = set(living_bu_dict.values())

    filtered_set = set(b for b in living_bu_set if b.type == bu_copy.type)
    # order the BUs by date of birth
    ordered_bu = sorted(filtered_set, key=lambda x: x.life.events['birth'])
    # note that sorted returns a copy, not a pointer to original BUs
    bu_count = len(ordered_bu)

    if number > bu_count:
        print('Killing more BUs than there are alive!')
        raise IndexError

    remaining = bu_count
    kill_index = 0
    # Right now this works, but makes it so that earliest unit is always killed
    # first, but at a death date that's in the middle of the range.
    # Does makes sense in real life that oldest unit dies 1st though...

    for i in range(number):
        kills_needed = number - i
        interval = remaining/kills_needed
        print("Kill Index" ,kill_index)
        kill_id = ordered_bu[kill_index].id.bbid
        target_bu = living_bu_dict[kill_id]
        target_bu.tag('killed')
        target_bu.kill(time_interval * i + date_index)
        remaining = bu_count - kill_index - 1
        kill_index += round(interval)

