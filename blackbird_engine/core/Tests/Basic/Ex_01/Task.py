#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests\\Basic\\Ex_01\Task

#***USE LOTS OF PRINT STATEMENTS***

"""
Agenda:

Basic extrapolate
Load sample model (filled out and all)
Move current period fwd 1 yr, 2 yrs, 3 yrs
Move current period back 1 yr, 2 yrs, 3 yrs
store in output
serialize updated model

Grader checks that bu_directory has the same keys for every period
Grader checks equality?? 
"""





import dill





output = {}

def do():
    return output
#
c = """

Running Extrapolate_01

Test evaluates whether extrapolate methods run.

Task loads a simple standard model with a developed top business unit. Task then
extrapolates the current period to periods 1, 2, and 3 years away, both forward
and back. Task relies on TimeLine methods to locate the appropriate target
periods.

At the conclusion of Task, the Model has 7 periods with filled out content. Task
stores the Model for Grader. Grader will check that every period contains the
same set of business units and evaluate each unit for equality with its other
versions. 
"""
print(c)
#
#T15.01: Load model, locate time periods
print("#T15.01: Load model")
output["T15.01"] = {}
print(output)
p = r"Tests\Basic\Ex_01\source_model.pkl"
print(p)
f = open(p,"rb")
print(f)
sM = dill.load(f)
f.close()
print("starting model: \n",sM)
p_ref = sM.currentPeriod
s_topBU = p_ref.content
print("""
p_ref = sM.currentPeriod
s_topBU = p_ref.content
""")
s_topBU.fillOut()
print("s_topBU.fillOut() \n")
print("top business unit: \n", s_topBU)
#
#target periods:
p_fwd1 = sM.timeLine.findPeriod("2016-03-30")
p_fwd2 = sM.timeLine.findPeriod("2017-03-30")
p_fwd3 = sM.timeLine.findPeriod("2018-03-30")
p_back1 = sM.timeLine.findPeriod("2014-03-30")
p_back2 = sM.timeLine.findPeriod("2013-03-30")
p_back3 = sM.timeLine.findPeriod("2012-03-30")
print("""
#target periods:
p_fwd1 = sM.timeLine.findPeriod("2016-03-30")
p_fwd2 = sM.timeLine.findPeriod("2017-03-30")
p_fwd3 = sM.timeLine.findPeriod("2018-03-30")
p_back1 = sM.timeLine.findPeriod("2014-03-30")
p_back2 = sM.timeLine.findPeriod("2013-03-30")
p_back3 = sM.timeLine.findPeriod("2012-03-30")
""")
#
#T15.02: Extrapolate reference period to each of target periods

c = ""
c += "T15.02: Extrapolate reference period to each of the six target periods."
print(c)
output["T15.02"] = {}
target_periods = [p_fwd1,p_fwd2,p_fwd3,p_back1,p_back2,p_back3]
print("""
output["T15.02"] = {}
target_periods = [p_fwd1,p_fwd2,p_fwd3,p_back1,p_back2,p_back3]
""")
print("""
About to run the following logic:

##for targ in target_periods:
##    orig_key = "orig " + str(targ.end_date)
##    output["T15.02"][orig_key] = targ
##    p_exed = p_ref.extrapolate_to(targ)
##    exed_key = "exed " + str(targ.end_date)
##    output["T15.02"][exed_key] = p_exed
##    sM.timeLine.addPeriod(p_exed)
##    #overwrites the old period
\n
""")
for targ in target_periods:
    print("\\targ:        \n%s" % targ)
    orig_key = "orig " + str(targ.end_date)
    print("\torig_key:    %s" % orig_key)
    output["T15.02"][orig_key] = targ
    print("""\toutput["T15.02"][orig_key] = targ""")
    p_exed = p_ref.extrapolate_to(targ)
    print("\tp_exed = p_ref.extrapolate_to(targ)")
    print("\tid(p_exed): %s" % id(p_exed))
    print("\tid(targ):   %s" % id(targ))
    print("\tid(p_ref):  %s" % id(p_ref))
    exed_key = "exed " + str(targ.end_date)
    output["T15.02"][exed_key] = p_exed
    print("\texed_key:   %s" % exed_key)
    print("""\toutput["T15.02"][exed_key] = p_exed""")
    sM.timeLine.addPeriod(p_exed)
    #overwrites the old period
    c = ""
    c += """\tsM.timeLine.addPeriod(p_exed)\n"""
    c += """\t#overwrites the old period\n\n"""
    print(c)
#
output["T15.02"]["M"] = sM
print("""output["T15.02"]["M"] = sM""")
#
p_u = r"tests\basic\Ex_01\updated_model.pkl"
#use relative paths to maintain portability; root directory is Diagnostics,
#where testing script is likely to run in the first place. 
f_new = open(p_u,"wb")
dill.dump(sM,f_new)
f_new.close()
#
print("Successfully completed test.")













