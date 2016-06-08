#BB Exceptions Module

#Custom Exception objects:
class BlackbirdError(Exception):
    #parent class for all custom errors defined for the Blackbird Environment
    pass

class BookMarkError(BlackbirdError):
    #used to alert missing bookmarks
    pass

class StructureError(BlackbirdError):
    pass

class IOPMechanicalError(StructureError):
    #raise if a test reveals that something is coded in a way that's not
    #intended
    pass

class AccountingError(BlackbirdError):
    pass

class ValueFormatError(AccountingError, TypeError):
    pass

class ManagedAttributeError(BlackbirdError):
    pass

class AbstractMethodError(BlackbirdError):
    pass

class BBAnalyticalError(BlackbirdError):
    """
    Parent class of custom exceptions raised during Blackbird analytical
    operations. I.e., topic selection, topic processing, topic definition
    """
    pass

class LifeCycleError(BBAnalyticalError):
    """
    Blackbird life cycle model cannot fit data.
    """
    pass

class PortalError(BlackbirdError):
    """
    Parent Exception class for Portal-related exceptions
    """
    pass

class QuestionFormatError(PortalError):
    """
    Question specifies a type or attribute that Portal does not understand.
    """
    pass

class ResponseFormatError(PortalError):
    """
    User provided a response that does not fit question or input type.
    """
    pass

class UserInterrupt(PortalError):
    """
    User entered "stop interview"
    """
    pass

class DefinitionError(BBAnalyticalError):
    """
    Exception for problems with object definition.
    """
    pass

class TopicDefinitionError(BBAnalyticalError):
    """
    Exception raised if Topic substance module lacks necessary attributes to
    become a functional Topic.
    """
    pass

class TopicOperationError(BBAnalyticalError):
    """
    Exception raised if Topic cannot perform desired analysis for some reason.
    """
    pass

class CatalogError(BBAnalyticalError):
    """
    Exception raised if a catalog finds a structural issue.
    """
    pass

class ExcelPrepError(BBAnalyticalError):
    """
    Exception signals issue with an Excel-oriented prep operation.
    """
    pass

class TagRegistrationError(CatalogError):
    """
    """
    content = "Tag already registered"

class ProcessError(IOPMechanicalError):
    content = "Improper process flow w/in BB environment."

class IDError(BBAnalyticalError):
    """
    High-level exception for any problems related to uuids within Blackbird.
    """
    pass

class IDAssignmentError(IDError):
    """
    Used when an object fails to assign a bbid where expected.
    """
    pass
class IDCollisionError(IDError):
    """

    """
    content = "The assigned UUID is the same as another in the active namespace"

class IDNamespaceError(IDError):
    """
    """
    content = "Object UUID not in the object's namespace UUID."

class ExcelPrepError(BlackbirdError):
    #used to alert missing bookmarks
    pass

class LinkError(BlackbirdError):
    content = "This Link has been intentionally broken during a path copy."

class BBPermissionError(BlackbirdError):
    content = "Operation violates the BB system of write permissions."
    
class ExternalDataError(BlackbirdError):
    """
    Exception class for outside data connectivity.
    """
    pass

