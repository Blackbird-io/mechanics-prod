# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.bundle
"""

Module defines Bundle class, a mix-in for managing objects whose attributes have
similar interfaces.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Bundle                Mix-in class for objects with symmetric attribute values
====================  ==========================================================
"""




# Imports
import copy




# Constants
# n/a

# Classes
class Bundle:
    """
    
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    ORDER                 tuple; standard processing order
    ordered               list; all statements in ORDER, built dynamically

    FUNCTIONS:
    copy()                return deep copy
    run_on_all()          perform arbitrary action on all defined statements
    ====================  ======================================================
    """
    ORDER = tuple()
    # tuple for immutability
    
    def __init__(self):
        pass
    
    def __str__(self):
        """


        Bundle.__str__() -> str

        
        Concatenate all defined statements into one string.
        """
        result = ""
        for statement in self.ordered:
            if statement is not None:
                result += str(statement)
            
        return result
    
    @property
    def ordered(self):
        """


        **read-only property**


        Return list of attribute values for all names in instance.ORDERED.
        """
        result = []
        for name in self.ORDER:
            statement = getattr(self, name)
            result.append(statement)
        #
        return result

    def copy(self):
        """


        Bundle.copy() -> Bundle


        Return a deep copy of instance.

        Method starts with a shallow copy and then substitutes deep copies
        for the values of each attribute in instance.ORDER
        """
        new_instance = copy.copy(self)
        
        for name in self.ORDER:
            own_statement = getattr(self, name, None)
            if own_statement is not None:
                new_statement = own_statement.copy()
                setattr(new_instance, name, new_statement)
            
        return new_instance
    
    def reset(self):
        """


        Bundle.reset() -> None


        Reset each defined statement. 
        """
        self.run_on_all("reset")

    def run_on_all(self, action, *kargs, **pargs):
        """


        Bundle.run_on_all() -> None

        
        Run ``statement.action(*kargs, **pargs)`` for all defined statements
        in instance.ordered.

        Expects ``action`` to be a string naming the statement method.
        """
        for statement in self.ordered:
            if statement is not None:
                routine = getattr(statement, action)
                routine(*kargs, **pargs)

    def summarize(self):
        """


        Bundle.summarize() -> None


        Summarize each defined statement.
        """
        self.run_on_all("summarize")
            
    #<------------------------------------------------------------------------need to inherit tags from statements?   
    
