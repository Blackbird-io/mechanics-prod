# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.system.bbid
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




#imports
import uuid




#globals
origin_s = "e6f3133e-b916-11e4-a4bf-ed7777fec77d"
BB_UUID_NAMESPACE = uuid.UUID(origin_s)

#classes
class ID:
    """

    Class provides an ID interface for Blackbird objects. All ids in the
    environment descend from the origin ID via uuid.uuid3() methodology.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bbid                  uuid; instance-specific uuid
    namespace             uuid; returns either instance-specific or origin
    origin_id             uuid; BB_UUID_NAMESPACE
    short                 string w prefix and last 4 symbols of bbid, or None

    FUNCTIONS:
    assign()              assigns the object a new uuid of instance.id_type
    revert_namespace()    undoes last change to instance.namespace_id
    set_namespace()       sets an external uuid as the instance's namespace
    verify()              see if bbid matches seed encoded in current namespace
    ====================  ======================================================
    """
    origin_id = BB_UUID_NAMESPACE

    def __init__(self, id_type=3):
        self.bbid = None
        #
        self._id_type = id_type
        self._prior_namespace = None
        self._namespace = None

    def __str__(self):
        return self.bbid.hex

    @property
    def namespace(self):
        """


        **read-only property**


        Return instance namespace or, if None, origin_id. Set through method.
        """
        result = self._namespace or self.origin_id
        return result

    class _TailDescriptor:
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

    short = _TailDescriptor()

    def assign(self, seed):
        """


        ID.assign() -> None


        Method assigns instance a UUID within the instance's namespace. Default
        namespace is the origin.

        ``seed`` should be a fixed external alphanumeric sequence (string or
        float) that describes the object in a way that humans can understand.
        To ensure that the ID is the same across runtimes, ``seed`` should be
        a constant fixed outside the method call.

        NOTE: users should **NOT** choose seeds that are ip/memory addresses,
        time, random numbers or hardware identifiers, among others.
        """
        encoder_name = "uuid" + str(self._id_type)
        # Pick up either uuid.uuid3, uuid.uuid4, or uuid.uuid5.
        encoder = getattr(uuid, encoder_name)
        self.bbid = encoder(self.namespace, seed)

    def revert_namespace(self):
        """


        ID.revert_namespace() -> None


        Undo-style method that sets instance.namespace_id to the value stored in
        last_namespace_id. After reverting, method clears last_namespace_id
        (sets the attribute to None).

        No-op if last_namespace_id is empty.
        """
        if self._prior_namespace:
            self._namespace = self._prior_namespace
            self._prior_namespace = None

    def set_namespace(self, new_namespace):
        """


        ID.set_namespace() -> None


        Method sets the instance's namespace_id to the argument. Preserves last
        namespace_id value, if specified, as last_namespace_id.
        """
        if self.namespace:
            self._prior_namespace = self.namespace
        self._namespace = new_namespace

    def verify(self, seed):
        """


        ID.verify() -> bool


        False if instance.bbid not what you get from uuid of the current type.
        True if it is.
        """
        result = False

        encoder_name = "uuid" + str(self._id_type)
        # Pick up either uuid.uuid3, uuid.uuid4, or uuid.uuid5.
        encoder = getattr(uuid, encoder_name)

        correct_id = encoder(self.namespace, seed)
        if self.bbid == correct_id:
            result = True

        return result

    @classmethod
    def from_database(cls, portal_data):
        """

        ID.from_database(portal_data) -> ID

        **CLASS METHOD**

        Method extracts ID from portal_data.
        """
        new = cls()
        new.bbid = uuid.UUID(portal_data)
        return new

    def to_database(self):
        """

        TimeLine.to_database() -> dict

        Method yields a serialized representation of self.
        """
        return self.bbid.hex
