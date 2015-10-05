#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: ColorManager.__init__
"""

ColorManager builds and administers a catalog of market color snapshots from
content modules in ColorWarehouse. The module follows the usual manager pattern:
it defines a construction routine for transforming static, usually primitive,
content data into richer run-time objects, and then stores the results in a
Catalog instance.

The color management system has some unique features:
1. each color content module describes market conditions as of a certain
   ``reference date``;
2. we identify content modules solely by the reference date; color content
   doesn't support tags;
3. when applying market color, topics always look for snapshot closest to
   the model's reference date. this selection criterion is simple and linear.
   blackbird does not need to compare the merits of 2+ color modules to figure
   out which is best for a given model.
4. we always describe the market in the same format. accordingly, content
   modules for market color are very simple.

ColorManager reflects these characteristics. Most significantly, it assigns
snapshots their BBID's based on the snapshot's reference date string.

ColorManager then stores snapshot BBIDs in local_catalog.by_name **under the
snapshot's ref_date**. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
catalog               instance of Catalog; by_name keyed by ref_date object
id                    instance of ID; bbid set to "ColorManager"

FUNCTIONS:
get_color()           pull copy of freshest color from catalog
make_color()          create a MarketColor object from a content module
populate()            walk warehouse, record all content in catalog

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBExceptions

from data_structures.system.protected_catalog import ProtectedCatalog
from data_structures.system.bbid import ID
from tools.for_calendar import find_most_recent
from tools.for_managers import walk_package

from . import ColorWarehouse as Warehouse




#globals
id = ID()
id.assignBBID("ColorManager")
local_catalog = ProtectedCatalog()

#functions
def get_color(query_date):
    """


    get_color(query_date) -> obj

    
    Function returns copy of freshest catalog content for query date.

    ``query_date`` should be a datetime.date object.
    """
    result = None
    #
    known_dates = local_catalog.by_name.keys()
    ref_id = find_most_recent(query_date, known_dates)
    result = local_catalog.issue(ref_id)
    #
    return result
        
def make_color(content_module, catalog = local_catalog, fill_gaps = False):
    """


    make_color(content_module
      [, catalog = local_catalog [, fill_gaps = False]]) -> None


    Function creates a copy of content module's ``color`` attribute,
    assigns the copy an id within the ColorManager namespace, and stores the
    copy in the catalog. If ``fill_gaps`` is True, function merges new snapshot
    with most recent existing data by retaining any old values the new color did
    not explicitly overwrite. 
    """
    new_color = content_module.color.copy()
    #
    if fill_gaps:
        last_known_date = find_most_recent(color.date)
        last_known_color = get_color(last_known_date)
        #
        filled_color = new_color.copy()
        #make the container and pick up any new attributes
        filled_color.update(last_known_color)
        filled_color.update(new_color)
        #add old content first, then overwrite w new content
        new_color = filled_color
    #
    if new_color:
        new_color.id.setNID(id.namespace_id)
        new_color.id.assignBBID(new_color.ref_date.isoformat())
    else:
        raise BBExceptions.CatalogError
        #somehow failed to create a color object
    #
    catalog.register(new_color, new_color.ref_date)

def populate():
    """


    populate() -> None


    Function walks the warehouse and applies make_color() to every module
    that specifies color_content to be True. Function then marks local_catalog
    as populated.

    To avoid key collisions on parallel imports, populate() performs a no-op
    if catalog is already populated. 
    """
    if not local_catalog.populated:
        snapshot_count = walk_package(Warehouse, "color_content", make_color)
        local_catalog.populated = True
        c = ""
        c += "ColorManager successfully populated catalog with %s market"
        c += " snapshots."
        c = c % snapshot_count
        print(c)
    else:
        pass
