#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FormulaWarehouse.Financials.IS.Revenue.MonthlyUnitRevenue.__init__
"""

Content module that defines a formula function that allows a driver to modify
a business unit. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
date_created          str in "YYYY-MM-DD"l; date when author wrote module
formula_content       bool; always True for content modules, else catalog skips
formula_author        str; name of person who wrote the module
name                  str; name of formula defined by module

FUNCTIONS:
func()                modifies line and /or business unit on behalf of driver

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a




#globals
formula_content = True
name = "monthly unit revenue over lifecycle."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-02"
required_data = ["annual_rev_per_mature_unit"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line value to 1/12th the annual unit revenue, adjusted for
    life stage. Function assumes that during growth stage, revenue ratably
    scales from 0 to mature amount, and that during decline stage, revenue
    ratably scales from mature amount to 0.

    Data must include:

    "annual_rev_per_mature_unit" 
    
    """
    # Default Excel output
    excel_template = "={life[alive]} * {parameters[annual_rev_per_mature_unit]}/12"
    cell_comment = ""
    line_references = dict()
    # Formula should build references dynamically at runtime, so that Chef
    # can use the objects themselves to locate cell coordinates.

    bu = business_unit

    # New (v.1.6.0) Life version analysis
    KEY_MATURITY = bu.life.KEY_MATURITY
    KEY_OLD_AGE = bu.life.KEY_OLD_AGE

    stage_name = None
    stage_start = None
    stage_end = None

    xl_stage_start = None
    xl_stage_end = None

    ref_date = bu.life.ref_date

    if bu.life.alive:
        stage_name = "youth"
        stage_start = 0
        stage_end = bu.life.PERCENT_MATURITY
        # Assume youth until we know otherwise

        xl_stage_start = "0"
        xl_stage_end = str(stage_end)
##        xl_stage_end = "+{life[PERCENT_MATURITY]}"

        if bu.life.events[KEY_MATURITY] <= ref_date:
            # Upgrade to maturity if appropriate.
            stage_name = "maturity"
            stage_start = stage_end
            stage_end = bu.life.PERCENT_OLD_AGE

            xl_stage_start = xl_stage_end
##            xl_stage_end = "+{life[PERCENT_OLD_AGE]}"
            xl_stage_end = str(stage_end)


        if bu.life.events[KEY_OLD_AGE] <= ref_date:
            # Upgrade further to decline. Use old label so we can keep next
            # block of old logic intact.
            stage_name = "decline"
            stage_start = stage_end
            stage_end = 100

            xl_stage_start = xl_stage_end
            xl_stage_end = "100"

    # Old (pre v.1.6.0) application
    if stage_name is None:
        pass
    else:
        annual_revenue = data["annual_rev_per_mature_unit"]
        monthly_revenue = annual_revenue / 12

##        excel_template = "={parameters[annual_rev_per_mature_unit]}/12"

        if stage_name == "maturity":
            line.setValue(monthly_revenue, driver_signature)
        elif stage_name == "youth":
            growth_adjustment = (business_unit.life.percent /
                                 (stage_end - stage_start))
            adj_growth_revenue = growth_adjustment * monthly_revenue
            line.setValue(adj_growth_revenue, driver_signature)

            xl_growth = "*{life[percent]}/("+xl_stage_end+"-"+xl_stage_start+")"
            excel_template += xl_growth

        elif stage_name == "decline":
            decline_adjustment = ((100 - business_unit.life.percent) /
                                  (stage_end - stage_start))
            adj_decline_revenue = decline_adjustment * monthly_revenue
            line.setValue(adj_decline_revenue, driver_signature)

            xl_decline = "*(100-{life[percent]})/("+xl_stage_end+"-"+xl_stage_start+")"
            excel_template += xl_decline


##    #--------------------------------------------------------------------------
##    #                   EXCEL FORMULA FORMATTING FOLLOWS                      |
##    #--------------------------------------------------------------------------
##    #
##    # The string composition logic below gradually builds up a large formula
##    # that tracks the Python func() calculation in a single Excel cell.
##    #
##    # Ideally, the results should be a string representing a VBA routine that
##    # the formula and chef can format with references and other data and add
##    # to the right cell. As a second-best alternative, formulas should be
##    # able to deliver multiple rows of dynamic calculation that build on each
##    # other in steps.
##    #
##    # We block old template construction logic here.
##
##    xl_birth = "{events[" + bu.life.KEY_BIRTH + "]}"
##    xl_maturity = "{events[" + KEY_MATURITY + "]}"
##    xl_old_age = "{events[" + KEY_OLD_AGE + "]}"
##    xl_death = "{events[" + bu.life.KEY_DEATH + "]}"
##
##    alive_condition = "=IF({life[alive]}, %s)"
##    youth_condition = "IF(AND({life[ref_date]}<" + xl_maturity + "), %s, %s)"
##    # have to be born for unit to be alive
##
##    mature_condition = "IF(AND(" + xl_maturity
##    mature_condition += "<={life[ref_date]}, {life[ref_date]}<" + xl_old_age + ", %s, %s)"
##
##    x_growth = "*ROUND({life[age]}/(" + xl_maturity + "-" + xl_birth + "), 0)*100"
##    x_decline = "*ROUND(({life[span]}-{life[age]})/(" + xl_death + "-" + xl_old_age + "),0)*100"
##
##    core = "+{parameters[annual_rev_per_mature_unit]}/12"
##
##    decline_calc = core + x_decline
##    growth_calc = core + x_growth
##
##    mature = mature_condition % (core, decline_calc)
##    youth = youth_condition % (growth_calc, mature)
##    full = alive_condition % youth
##
##    excel_template = full
##    line_references = dict()


    # Always return excel_template, references
    return excel_template, cell_comment, line_references
