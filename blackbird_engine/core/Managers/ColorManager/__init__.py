#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FormulaManager.__init__
"""

Module builds and administers a catalog of formulas from content modules in
FormulaWarehouse.

The Modelling.Driver module imports FormulaManager and populates the catalog.
From there, FormulaManager primarily serves Driver operations. The
FormulaManager serves a secondary, supporting role for TopicManager, where
FormulaManager delivers actual Formula objects that Topics can use in the
drivers they create. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
catalog               instance of Platform.Catalog;by_name also keyed by func
id                    instance of Platform.ID; bbid set to "FormulaManager"

FUNCTIONS:
make_formula()        create a Formula object from a content module
populate()            create and record all Topics in TopicWarehouse in catalog               

CLASSES:
n/a
====================  ==========================================================
"""

#comments on MarketColorManager
#warehouse organized by month, by year
#2014/01-2014, 02-2014, etc.
#modules named the date, in mcYYYYMMDD format

#each module configures an instance of MarketColor; instance stored at .color

#manager walks the warehouse and enters the .color value into the catalog
#could have manager fill out .color w any keys from last date that arent in color already
##so if we have og&c in one period and the next period doesn't include it
##parameter called ``guess``


#catalog is just a dictionary?
    #can also be an instance of time_line
    #need to be able to pull out closest date
        #only look back
        #kind of a simple algo:
            #set of keys
            #add query date
            #sort into list
            #index query date
            #pull out i -1
            #
#use regular dictionary
    #to start, won't have "forecasted" future color?
    #can add later if necessary

#CM has a ``current`` attribute or something that uses ?
    #but Globals.ref_date is inevitably static, so ... kind of pointless to make it pseudo-dynamic
    #should just be explicit about what you are calling

#should go on topic

#conclusions:
    #use regular catalog
    #add some methods

#imports
import BBExceptions
import Tools.ForManagers

from DataStructures.Platform.Catalog import Catalog

from . import ColorWarehouse as Warehouse




#globals
local_catalog = Catalog()
id = ID()
id.assignBBID("ColorManager")

#functions

def find_prior_date(query_date):
    """
    returns the most recent matching date
    #
    #<--------------------------------------------------------------------can pull this out into Tools???
    #describe search algo [relies on sort]
    #[make sure sort is from oldest to newest]
    """
    last_known = None
    known_color = set(local_catalog.by_name.keys())
    if query_date in known_color:
        last_known = query_date
    else:
        w_query = known_color.add(query_date)
        w_query = sorted(w_query)
        i_query = w_query.index(query_date)
        if i_query == 0:
            raise ColorError
            #no known color prior to query date
            #pick later date or turn allow_future to True
        else:
            i_prior = i_query - 1
            last_known = w_query[i_prior]
    #
    return last_known    

def get_color(query_date):
    #gets bbid
    #gets catalog to iss
    #returns color module that you can use
    result = None
    #
    bbid = find_known_date(query_date)
    result = local_catalog.issue(bbid)
    #
    return result
    
def get_latest():
    result = None
    latest_date = max(local_catalog.by_name.keys())
    latest_id = local_catalog.by_name[latest_date]
    result = local_catalog.issue(latest_id)
    #
    return result
    
def make_color(content_module, catalog = local_catalog, fill_gaps = False):
    """

    #fill out doc string <-------------------------------------------------------------
    
    """
    new_color = content_module.color.copy()
    if fill_gaps:
        last_known_date = find_known_date(color.date, allow_future = False)
        last_known_color = get_color(last_known_date)
        #
        filled_color = last_known_color.copy()
        #take old content
        filled_color.update(new_color)
        #overwrite old content w new content
        new_color = filled_color
        #reassign name
    #
    if new_color:
        new_color.id.setNID(id.namespace_id)
        new_color.id.assignBBID(new_color.as_of.isoformat())
    else:
        raise BBExceptions.CatalogError
        #somehow failed to create a color object
    #
    catalog.register(new_color, filled_color.as_of.isoformat())

def populate():
    """


    populate() -> None


    [Function walks the TopicWarehouse and applies make_topic() to every module
    that specifies topic_content to be True. Function then marks local_catalog
    as populated.

    To avoid key collisions on parallel imports, populate() performs a no-op
    if catalog is already populated.] 
    """
    if not local_catalog.populated:
        snapshot_count = Tools.ForManagers.walk_package(Warehouse,
                                                        "color_content",
                                                        make_color)
        local_catalog.populated = True
        c = ""
        c += "ColorManager successfully populated catalog with %s"
        c += " market snapshots."
        c = c % snapshot_count
        print(c)
    else:
        pass
