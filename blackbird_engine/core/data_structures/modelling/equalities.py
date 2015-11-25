#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.equalities
"""

Module defines Equalities class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
tabbed_print          utility function for tracing equality analysis

CLASSES:
Equalities

====================  ==========================================================
"""




#imports
import inspect

import bb_settings




#globals
#n/a

#functions
def tabbed_print(s,tw):
    """

    tabbed_print(s,tw) -> None

    Expands tabs on string ``s`` to width ``tw``, prints result.
    """
    s = s.expandtabs(tw)
    print(s)

#classes
class Equalities:
    """

    Mix-in class that overloads __eq__ and __ne__ methods
      Eq.__eq__() performs all of the evaluataion work
      Eq.__ne__() always returns the boolean negative of Eq.__eq__()

    If ``keyAttributes`` are specified on an instance or descendant class,
    Equalities.__eq__() will only check parity across the specified attributes.
    Otherwise, method will check parity across all attributes found by running
    dir(instance).

    When performing comparison, Equalities.__eq__() will skip any attributes
    starting with a string in ``irrelevantAttributes`` (originally intended for
    exact matches only) or ``skipPrefixes``. Match against both lists uses
    string.startswith() to optimize for speed.
    
    NOTE: parentObject and other attributes that hook to objects w overloaded
    __eq__ may cause infinite loops.

    For example, to compare two objects with a ``parentObject`` attribute,
    Eq.__eq__() evaluates A.parentObject == B.parentObject. If ``parentObject``
    in either A or B overloads __eq__ using this Equalities class, the A.__eq__
    evaluation will run parentObject.__eq__. To the extent parentObject is a
    list or other container, parentObject.__eq__ will cycle through each item in
    said container. If A is in the container, A.parentObject.__eq__ will then
    call A.__eq__, closing the loop. Other loop forms are possible too.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    keyAttributes         None; list of attribute names that should be compared
    irrelevantAttributes  list; list of attribute names that should not be
                          compared
    skipPrefixes          list; list of prefixes that mean an attribute should
                          not be compared
    ignoreSystem          bool; ignore system attributes
    
    FUNCTIONS:
    __eq__()              goes through all attributes and contents, returns bool
    __ne__()              returns not Eq.__eq__()

    ====================  ======================================================
    """
    keyAttributes = None
    irrelevantAttributes = []
    skipPrefixes = []
    ignoreSystem = True

    def __init__(self):
        pass
    
    def __eq__(self, comparator, trace = False, tab_width = 4):
        """


        Equalities.__eq__(comparator[,trace = False]) -> bool


        Provides a boolean result to equality (==) tests against comparator.

        bool is True if every non-system attribute of self equals the same
        attribute of comparator. If instance is descended from a list, method
        checks whether each item in self equals to the matching position in
        the comparator. If instance is descended from a dictionary, method
        checks whether instance and comp have the same keys and values.

        Method uses builtins.isinstance() to check for list or dict ancestry.
        Method uses inspect.isfunction() and inspect.ismethod() to skip callable
        attributes. 
        """
        result = True
        #
        lType = False
        dType = False
        sameProfile = True
        tw = tab_width
        tw_arg = tw+4
        tw_element = tw_arg
        #
        #Part 1: Compare attributes
        #
        #Part 1.1: Identify which attributes to compare
        skipNames = self.skipPrefixes + self.irrelevantAttributes + ["__"]
        skipNames = tuple(skipNames)
        if trace:
          dashes = "\t"+ "-"*(bb_settings.SCREEN_WIDTH - tab_width*2)+"\n" 
          t_header = ""
          t_header += dashes
          t_header += "\tBegin tracing equality evaluation...\n"
          t_header += "\t  object:     %s\n" % self
          t_header += "\t  comparator: %s\n\n" % comparator
          tabbed_print(t_header,tw)
          p_skip_names = "\tskipNames: \n\t%s\n" % str(skipNames)
          tabbed_print(p_skip_names,tw)
        attrsToReview = []
        if self.keyAttributes != None:
            attrsToReview = self.keyAttributes
        else:
            attrsToReview = dir(self)
        if trace:
            p_attrs_rev = "\tattrsToReview: \n"
            for attr in attrsToReview:
                p_attrs_rev += "\t  %s\n" % attr
            tabbed_print(p_attrs_rev,tw)
        #Upgrade_S: First, take a set difference of attrsToReview and skipNames
        #then sort, then go through more detailed analysis
        #
        #Part 1.2: Retrieve and compare attribute values.
        for testattr in attrsToReview:
            if trace:
                p = "\tchecking attr: ``%s``" % testattr
                tabbed_print(p,tw_arg)
            if testattr.startswith(skipNames):
                if trace:
                    p = "\tattribute in skipNames, continue\n"
                    tabbed_print(p,tw_arg)
                continue
            else:
                #check that attribute is not a method
                standardValue = getattr(self,testattr)
                if trace:
                    p = "\t  standard value: %s" % standardValue
                    tabbed_print(p,tw_arg)
                if inspect.isroutine(standardValue):
                    if trace:
                        p = ""
                        p += "\t  ``%s`` is a routine (according to inspect).\n"
                        p += "\tcontinue\n"
                        p = p % testattr
                        tabbed_print(p,tw_arg)
                    continue
                #make sure the comparator has an attribute of the same name
                try:
                    compValue = getattr(comparator, testattr)
                    if trace:
                        p = "\t  comp value:     %s" % compValue
                        tabbed_print(p,tw_arg)
                except AttributeError as E:
                    result = False
                    if trace:
                        p = ""
                        p += "\t  comp value: AttributeError on getattr()\n"
                        p += "\t  %s\n" % E
                        p += "\t  break\n"
                        tabbed_print(p,tw_arg)
                    break
                #
                #both objects have the same attribute. now compare values. if
                #``trace`` is off, use simple comparison. if ``trace`` is on,
                #try to make sure any attributes that support tracing during
                #equality evaluations report accordingly. so try to call the
                #the .__eq__(trace=True) method first, indented one level. if
                #that fails, run plain vanilla ``==`` (i.e., ``.__eq__()`` w no
                #keyword arguments).
                #
                if not trace:
                    if standardValue == compValue:
                        continue
                    else:
                        result = False
                        break
                else:
                    try:
                        if standardValue.__eq__(compValue, trace = True,
                                                tab_width = tw_arg):
                            p = ""
                            p += "\t  standardValue == compValue: True\n"
                            p += "\t(using .__eq__(trace=True))\n"
                            p += "\tcontinue\n"
                            tabbed_print(p,tw_arg)
                            continue
                        else:
                            p = ""
                            p += "\t  standardValue == compValue: False\n"
                            p += "\t(using .__eq__(trace=True))\n"
                            p += "\t  result = False\n"
                            p += "\tbreak\n"
                            tabbed_print(p,tw_arg)
                            result = False
                            break
                    except TypeError as X:
                        p = ""
                        p += "\tException on .__eq__(trace=True) call:\n"
                        p += "\t  %s\n" % X
                        p += "\tRunning plain vanilla ``==`` call..."
                        tabbed_print(p,tw_arg)
                        if standardValue == compValue:
                            p = ""
                            p += "\t  standardValue == compValue: True\n"
                            p += "\tcontinue\n"
                            tabbed_print(p,tw_arg)
                            continue
                        else:
                            p = ""
                            p += "\t  standardValue == compValue: False\n"
                            p += "\t  result = False\n"
                            p += "\tbreak\n"
                            tabbed_print(p,tw_arg)
                            result = False
                            break
        if trace:
            p = ""
            p += "\tattribute comparison completed.\n"
            p += "\tresult: %s\n" % result
            tabbed_print(p,tw)
        #
        #Part 2: Compare contents
        #
        #Part 2.1: Check whether object is a container. If it is, comparator
        #must descend from the same type. 
        #
        #Equalities is a mix-in class, so this method could be called from
        #a variety of different instances.
        if result:
            if isinstance(self,list):
                lType = True
                if not isinstance(comparator,list):
                    sameProfile = False
                    result = False
                    if trace:
                        p = ""
                        p += "\tObject is list-type, comparator is not.\n"
                        p += "\tresult = False\n"
                        tabbed_print(p,tw)
        else:
            return result
        if result:
            if isinstance(self,dict):
                dType = True
                if not isinstance(comparator,dict):
                    result = False
                    if trace:
                        p = ""
                        p += "\tObject is dict-type, comparator is not.\n"
                        p += "\tresult = False\n"
                        tabbed_print(p,tw)
        else:
            return result
        #Part 2.2: Object and comparator share relevant parts of their container
        #lineage. Compare their contents. 
        #
        #For speed, the sameProfile (like-type) contents comparison runs on the
        #built-in __eq__ for list and dict types. The built_in __eq__ won't call
        #.__eq__(trace=True), even if some of the items that object contatins
        #support equality tracing. Equality tracing is particularly important
        #when equality is False, since it helps a user pin down the source of
        #divergence. Therefore, as a stop-gap measure, when ``trace`` is True,
        #this method runs a secondary, slow item-by-item comparison that first
        #tries to call .__eq__(trace=True) directly, then uses the built-in
        #interface.
        #
        if result:
            if lType:
                result = list.__eq__(self,comparator)
                if trace and not result:
                    p = ""
                    p += "\tlist.__eq__(self,comparator) == False\n"
                    p += "\tRun list introspection logic.\n"
                    tabbed_print(p,tw)
                    #
                    orig_len = len(self)
                    comp_len = len(comparator)
                    p = ""
                    p += "\tobject length: %s\n" % orig_len
                    p += "\tcomparator length: %s\n" % comp_len
                    tabbed_print(p,tw)
                    if not orig_len == comp_len:
                        p = ""
                        p += "\torig_len == comp_len: False\n"
                        p += "No further analysis necessary."
                        tabbed_print(p,tw)
                    else:
                        p = ""
                        p += "\torig_len == comp_len: True\n"
                        p += "Compare item by item."
                        tabbed_print(p,tw)
                        together = enumerate(zip(self,comparator))
                        for (i, (orig_item,comp_item)) in together:
                            p = ""
                            p += "\tIndex %s:\n" % i
                            p += "\t  orig_item: %s\n" % orig_item
                            p += "\t  comp_item: %s\n" % comp_item
                            tabbed_print(p,tw_element)
                            try:
                                if orig_item.__eq__(comp_item, trace=True,
                                                    tab_width = tw_element):
                                    p = ""
                                    p += "\torig_item == comp_item: True\n"
                                    p += "\t(using .__eq__(trace=True))\n"
                                    p += "\tcontinue"
                                    tabbed_print(p,tw_element)
                                    continue
                                else:
                                    p = ""
                                    p += "\torig_item == comp_item: False\n"
                                    p += "\t(using .__eq__(trace=True))\n"
                                    p += "\tbreak"
                                    tabbed_print(p,tw_element)
                                    break
                            except TypeError as X:
                                p = ""
                                p += "\tException on .__eq__(trace=True) call:\n"
                                p += "\t  %s\n" % X
                                p += "\tRunning plain vanilla ``==`` call..."
                                tabbed_print(p,tw_element)
                                if orig_item == comp_item:
                                    p = ""
                                    p += "\torig_item == comp_item: True\n"
                                    p += "\tcontinue"
                                    tabbed_print(p,tw_element)
                                    continue
                                else:
                                    p = ""
                                    p += "\torig_item == comp_item: False\n"
                                    p += "\t(using .__eq__(trace=True))\n"
                                    p += "\tbreak"
                                    tabbed_print(p,tw_element)
                                    break
                        else:
                            p = ""
                            p += "\tAll items compare equal.\n"
                            p += "\t... but this block should only run when "
                            p += "result is False...\n"
                            p += "\tsomething odd happening.\n"
                            tabbed_print(p,tw)
                            #can add double-check logic here
        if result:
            if dType:
                result = dict.__eq__(self,comparator)
                if trace and not result:
                    p = ""
                    p += "\tdict.__eq__(self,comparator) == False\n"
                    p += "\tRun dict introspection logic.\n"
                    tabbed_print(p,tw)
                    #
                    #check keys
                    #For dict to compare equal, all keys must be shared. Only
                    #run dict.__eq__ if both instance and comp descend from
                    #dictionaries, so both objects should have the keys method. 
                    ks_orig = set(self.keys())
                    ks_comp = set(comparator.keys())
                    ks_shared = ks_orig & ks_comp
                    ks_only_orig = ks_orig - ks_shared
                    ks_only_comp = ks_comp - ks_shared
                    if ks_only_orig:
                        p = ""
                        p += "\tinstance has keys that do not appear in"
                        p += "comparator\n"
                        p += "\tinstance-only keys: \n%s\n" % ks_only_orig
                        tabbed_print(p,tw)
                    if ks_only_comp:
                        p = ""
                        p += "\tcomparator has keys that do not appear in"
                        p += "instance\n"
                        p += "\tcomparator-only keys: \n%s\n" % ks_only_comp
                        tabbed_print(p,tw)
                    #
                    ks_shared = sorted(ks_shared)
                    #sort for stable order
                    p = ""
                    p += "\tinstance and comparator have identical keys. step "
                    p += "through each value and compare.\n"
                    tabbed_print(p,tw)
                    #                    
                    for k in ks_shared:
                        orig_val = self[k]
                        comp_val = comparator[k]
                        p = ""
                        p += "\tkey %s:\n" % k 
                        p += "\t  orig_val: %s\n" % orig_val
                        p += "\t  comp_val: %s\n" % comp_val
                        tabbed_print(p,tw_element)
                        try:
                            if orig_val.__eq__(comp_val, trace=True,
                                                tab_width = tw_element):
                                p = ""
                                p += "\torig_val == comp_val: True\n"
                                p += "\t(using .__eq__(trace=True))\n"
                                p += "\tcontinue"
                                tabbed_print(p,tw_element)
                                continue
                            else:
                                p = ""
                                p += "\torig_val == comp_val: False\n"
                                p += "\t(using .__eq__(trace=True))\n"
                                p += "\tbreak"
                                tabbed_print(p,tw_element)
                                break
                        except TypeError as X:
                            p = ""
                            p += "\tException on .__eq__(trace=True) call:\n"
                            p += "\t  %s\n" % X
                            p += "\tRunning plain vanilla ``==`` call..."
                            tabbed_print(p,tw_element)
                            if orig_val == comp_val:
                                p = ""
                                p += "\torig_val == comp_val: True\n"
                                p += "\tcontinue"
                                tabbed_print(p,tw_element)
                                continue
                            else:
                                p = ""
                                p += "\torig_val == comp_val: False\n"
                                p += "\t(using .__eq__(trace=True))\n"
                                p += "\tbreak"
                                tabbed_print(p,tw_element)
                                break
                    else:
                        p = ""
                        p += "\tAll values compare equal.\n"
                        p += "\t... but this block should only run when "
                        p += "result is False...\n"
                        p += "\tsomething odd happening.\n"
                        tabbed_print(p,tw)
                        #can add double-check logic here
        return result

    def __ne__(self,comparator, trace = False, tab_width = 4):
        """


        Equalities.__ne__(comparator[, trace = False, [tab_width = 4]]) -> bool


        Returns boolean negative of Equalities.__eq__(comparator)
        """
        eq = self.__eq__(comparator,trace,tab_wdith)
        result = not eq
        return result
