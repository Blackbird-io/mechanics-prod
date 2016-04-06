#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.system.catalog
"""

Module defines Catalog class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Catalog
====================  ==========================================================
"""




#imports:
import bb_exceptions




#globals
#n/a

#classes
class Catalog:
    """

    Class provides standard template for object catalogs. Catalogs allow human
    and machine users to rapidly locate a desired object. Blackbird catalogs
    generally key objects by bbid (type-3 uuid). 

    Because bbids look like random strings of 16 characters, humans generally
    find them unwieldy and meaningless. To make catalog content easy for human
    users to access, the Catalog object should also maintain a reverse look-up
    table that maps easy-to-read-and-remember attributes to object bbids.
    
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    by_id                       dict; bbid to object
    by_name                     dict; name or other attribute to bbid
    populated                   bool; has catalog been populated

    FUNCTIONS:
    issue()                     returns object with matching bbid
    register()                  adds object to by_id and by_name
    ==========================  ================================================
    """
    def __init__(self):
        self.by_id = {}
        self.by_name = {}
        self.populated = False

    def issue(self,bbid):
        """


        Catalog.issue(bbid) -> obj


        Method returns object with matching bbid.
        """
        result = self.by_id[bbid]
        return result

    def register(self, obj, *reverse_keys, overwrite = False):
        """


        Catalog.register(obj,*reverse_keys) -> None


        Method registers obj in instance.by_id under obj.id.bbid, and in
        instance.by_name under each key specified in reverse_keys. 
        """
        if not overwrite:
            if obj.id.bbid in self.by_id:
                c = "id collision in catalog\n"
                raise bb_exceptions.CatalogError(c, obj.id.bbid)
            overlap = set(reverse_keys) & set(self.by_name.keys())
            if overlap != set():
                c = "name key collision in catalog"
                raise bb_exceptions.CatalogError(c, overlap)
        self.by_id[obj.id.bbid] = obj
        for k in reverse_keys:
            if k:
                self.by_name[k] = obj.id.bbid
            else:
                #cannot register unintentionally under blank key
                c = ""
                c += "Catalog prohibits registration under None or other \n"
                c += "objects with False values."
                raise bb_exceptions.CatalogError(c)
