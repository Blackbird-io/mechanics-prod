#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: PlatformComponents.ID
"""

Module defines ID class. Goal of class is to provide unique, stable IDs to
objects within the Blackbird environment.

Blackbird IDs must be unique: if two objects are different and both use IDs,
their IDs must be different. If two objects share an ID, they are the ``same``
object (e.g., a user, a store, an account, etc.).

Blackbird IDs must be stable: running the same program multiple times must yield
the same IDs for the same objects. That is, the IDs for each object must compare
equal between runtimes. This requirement is essential for testing and
monitoring.

To implement the above requirements, Blackbird uses name-namespace UUIDs from
the built-in Python uuid module. All Blackbird uuids descend from a single
stable environment UUID.

To generate the seed UUID from scratch, run uuid.uuid1 on the original Blackbird
computer for the original go-live date. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
BB_UUID_NAMESPACE     seed UUID for the Blackbird environment
origin_s              string form of seed UUID 

FUNCTIONS:
n/a

CLASSES:
ID                    tracks namespace and object uuids
====================  ==========================================================
"""





import uuid





origin_s = "e6f3133e-b916-11e4-a4bf-ed7777fec77d"
BB_UUID_NAMESPACE = uuid.UUID(origin_s)

class ID:
    """

    Class provides an ID interface for Blackbird objects. All ids in the
    environment descend from the origin ID via uuid.uuid3() methodology.

    Client objects may set their own namespace_id. The default namespace_id is
    the origin UUID. It is stored on the class as namespace_id 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bbid                  uuid; instance-specific uuid
    id_type               int; class supports uuid-3,uuid-4, or uuid-5
    last_namespace_id     uuid; last specified namespace_id  
    namespace_id          uuid; instance or class state
    origin_id             uuid; BB_UUID_NAMESPACE
    short                 string w prefix and last 4 symbols of bbid, or None
    
    FUNCTIONS:
    assignBBID()          assigns the object a new uuid of instance.id_type       
    class dynamicShort    descriptor for short generation
    revertNID()           undoes last change to instance.namespace_id
    setNID()              sets an external uuid as the instance's namespace
    ====================  ======================================================
    """
    origin_id = BB_UUID_NAMESPACE
    namespace_id = origin_id
    
    def __init__(self,id_type = 3):
        self.bbid = None
        self.id_type = id_type
        self.last_namespace_id = None

    class dynamicShort:
        def __init__(self):
            self.chars = 4
            self.prefix = "xx"
            
        def __get__(self,instance,owner):
            result = None
            full = None
            if instance.bbid:
                full = str(instance.bbid)
                result = "xx" + full[-self.chars]
            return result
            
        def __set__(self,instance,value):
            pass

    short = dynamicShort()

    def assignBBID(self,name):
        """


        ID.assignBBID(name) -> None


        Method assigns instance a UUID within the instance's namespace. Default
        namespace is the origin.

        ``name`` should be a fixed external alphanumeric sequence (string or
        float) that describes the object in a way that humans can understand.
        To ensure that the ID is the same across runtimes, ``name`` should be
        a constant fixed outside the method call.

        NOTE: users should **NOT** choose names that are ip/memory addresses,
        time, random numbers or hardware identifiers, among others. 
        """
        if self.id_type == 3:
            self.bbid = uuid.uuid3(self.namespace_id,name)
        if self.id_type == 4:
            self.bbid = uuid.uuid4()
        if self.id_type == 5:
            self.bbid = uuid.uuid5(self.namespace_id,name)

    def verify(self,name):
        """


        ID.verify(name) -> bool


        False if instance.bbid not what you get from uuid of the current type.
        True if it is. 
        """
        result = False
        vid = None
        if self.id_type == 3:
            vid = uuid.uuid3(self.namespace_id,name)
        if self.id_type == 4:
            vid = uuid.uuid4()
        if self.id_type == 5:
            vid = uuid.uuid5(self.namespace_id,name)
        if vid == self.bbid:
            result = True
        return result

    def revertNID(self):
        """


        ID.revertNID() -> None


        Undo-style method that sets instance.namespace_id to the value stored in
        last_namespace_id. After reverting, method clears last_namespace_id
        (sets the attribute to None).

        No-op if last_namespace_id is empty. 
        """
        if self.last_namespace_id:
            self.namespace_id = self.last_namespace_id
            self.last_namespace_id = None
        

    def setNID(self,ns_uuid):
        """


        ID.setNID(ns_uuid) -> None


        Method sets the instance's namespace_id to the argument. Preserves last
        namespace_id value, if specified, as last_namespace_id.
        """
        if getattr(self,"namespace_id",None):
            self.last_namespace_id = self.namespace_id
        self.namespace_id = ns_uuid
        
        
    
    
    
