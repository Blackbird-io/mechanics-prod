"""
# Comments on excel output

# Derivation works best with spreading because formulas

                # can then look up parameters and other lines

                # If they only look up parameters, you can write the formulas as strings
                # to a list and then put the strings whereever, cause their referents
                # won't change. But some formulas will want to look at other lines and
                # potentially other periods. It's more difficult to do so if you don't know
                # where they are, though we could have some system that sets up pointers
                # to the input lines and then we resolve the pointers when we know where
                # they are. Like literally, the formula would deliver a string template
                # with a bunch of blank fields "{cost}.xl.final + {opex}.xl.final + {sga}.xl.final" and then an array of
                # objects (!): [a, b, c]  (or a dictionary: "cost" : a, "opex" : b, "sga" : c} and we would format the string at the appropriate time (once
                # we have completed those other things). A more explicit format like that
                # could actually prove useful as a comment in excel: we can literally take
                # the entire string and put it on as a comment (or only in the current column)
                #
                # We would still want to piggyback on the recursion cause otherwise difficult
                # to replicate the order of operations.
                #
                # The challenge with drivers is that they work in sequence and build on
                # existing values. And then update the xl.derived.final attribute to wherever
                # they finish. I guess we could make that operation automatic in the _spread()
                # function. 
                #
                # In the separate spread approach, each driver could append row-style entries to
                # a list. The entries should have a formula, a context dictionary, and a label.
                # Basically, up to a 3-column array. If the driver wants to use params, it can
                # specify those as well.
                #
                # The spreader function could then spread all those entries to a list. 
                #
                #   The issue is how to do incremental things. I guess could just point to line.xl.final
                #   and would have to be careful about when I increment them (ie, whatever the value was
                #   at that time). 
                #
                #   The outcome is basically the same cause you still get each one of the steps to
                #   generate a thing. Also, still expect the formula to use parameters, and those are still
                #   on the sheet. The difference is now you can organize the positions separate from
                #   the order of operations. 
                #
                #   Finally, if you point to other periods, ... kind of need to know what column they are in
                #   So the final coordinate has to have a row and a column.
                #
                #   Potentially allows much faster spreading because you make the formula once, its on the
                #   driver, and then you can apply it many times (copy the columns).
                #
                # One other challenge is inserting lines // when the periods differ from each
                # other. Here, you really would want to insert lines in the spreadsheet, because
                # you want to make sure you keep the alignment. 
                #
                # So driver would build up driver cells and put them on .xl.derived.rows
                #
                # and then the spreader would put all the cells in a particular order
                #
                # the spreader could be the one that assembles the details into the whole
                    # walks each line in each statement
                        # for detail in order:
                            # spreads line:
                                # consolidated results
                                # derived results
                                # detailed results
                            # adds summations for each, where appropriate
                        # 
                #
                # then the load_balance function can assign xl coordinates to the right cells

                # in terms of insertion:
                #   you have to move existing cells down if you are putting in a line that wasn't there in
                #   prior period in same position
                # 
                #   and you have to leave cells blank if you are missing a line
                #       otherwise you are going to be putting things in the wrong place
                #       could introduce ranges for this
                #        or line ids
                #        or something else
                #
                #   you also have to change a bunch of the formulas

# on bb_formula operations:

# formula should attach cells to the driver block
        #   or return cells to the driver
        #
        # can finally separate derive and spread (sort of)
        #   if formula looks to past periods, that's ok; formula can conduct
        #   complex search ops and that's ok too: can just add pointers to the
        #   results (hopefully). You won't see the search logic in excel, but
        #   you'll see the relationships. 
        #
        # for the vars it uses:
        #   driver can give it the dictionary of hard-coded addresses?
                # most natural
        #   or it can pass in the sheet

        #   or it can deliver a matrix of rows
        #     issue is that now at derive time, we dont know absolute position
        #     not entirely true: we know absolute position of parameters
        #
        # 
        #
        #   alternatively, driver can deliver a map 
        #
        # can start off by using hard-coded params within the formula
        # (or driver can add rows to a lookup; but dont want a huge thing)
        # 
        # ok come on lets do the skeleton
        #
        # formula expects to receive variables:
        #   NOT params
        #   so we have to give it row position associated with those variables anyways
        #
        #   driver carries some params and a map to change params into vars
        #   driver could deliver its params in a couple rows
        #   and the map
        #   formula could deliver its string
        #   we could then assemble the dictionary of row references at spread time
        #    # as in, could put the driver rows where they belong
        #    # copy the params range from the sheet, update it with the new rows
        #    # map the values in the range to keys in the conversion map, so we have rows associated with vars
        #    # and format the formula with those values
        #
        #  what if the formula string comes back with the following:
        #    # references: {}
        #    # parameters: {}
        #    and then you can key each one

        
        #   issue is that have to format twice, once for the params and once for the other stuff
        #    # could mush them together
        #    # really would be a LOT more elegant if we could eliminate the driver-level params
        #    # could give the sheet to the formula and get

        #   i want to get a formula like "={references}[line].xl.final * 1.03" or "=c4 * (1+{inflation})"
            # {line} requires a final position
            # inflation is just a parameter
            # and i m responsible for filling in the parameters later
            #
            # formula is going to deliver a string, a references dictionary
            # and then for params, im supposed to supply those
            #
            # basically need to separate driver-level parameters and larger ones
            #

# general principles:
    
    # Generally speaking, "current row" should always be empty. Each routine
    # should move the index to the right place when its done.

    When working on row insertion and deletion, it will generally be easier to
    build a new sheet from updated SheetData information, since you will have to
    re-do all of the formulas with references below your deletion/insertion target.



# To do:

 - control number of total sheets (max should be like ~200 or so)
   -- figure out what to do when model would exceed that number. could potentially
      route calculations through bb itself.
 - think about creating a Coordinates class in DataManagement,
   -- with a .row, .column, and .sheet attrs
   -- can be properties to make sure values always conform (e.g., column should
      always be a number or smtg, values should always be positive integers)
   -- can have .dict() method that returns a dictionary (or the instance __dict__

 - should probably apply formatting wholesale if possible:
   -- keep track of all hard-coded cells (by location with sheet); format them in one
      lump sum

 - figure out what to do with SheetData on save (may be find a place in the work book to put it? or
   at least delete it explicitly)

 - !figure out what to do about large or mutable parameter values

 - implement template relationships (ie, create a unit template, have units inherit
   from that template). Could provide an avenue for mutable structure work, because the templates
   only exist in a single period, so we could spread them over multiple cells.

   -- alternatives for mutable structures:
      --- compute things dynamically in python, a la xlwings

      --- if you have one of these things, you can flip the timeline into a vertical (so it goes
          by rows), and then spread the array across columns. You would deliver the results as
          an Excel array (into a single cell, probably), and expect the formula to include read
          logic for that thing.

          In this kind of parametrization, you could have mappings look like a key per row, with values
          being columns.

          in the period column, you could then merge the cells for all the keys, so when you are walking
          down that column, you always go period by period. or something like that.

      --- add excel named ranges for a similar approach to above.

      Probably want to do some combination. If you have a bunch of complex mapping data that requires
      sheet-like spread, Excel will probably run very slowly (since its all sequential vs random access).
      So probably better to manage in memory in Python. On the other hand, basic arrays are kind of
      not a big deal.
      
         Other issue is that this approach creates a new tab per fancy parameter. That can mean waaaay
         more tabs. Which again costs speed.

         Ideally, you probably want something like a BB Client running on your computer, that Excel
         can use for complex calculations. BB Main (online) could deliver Excel models with embedded Python
         (or C) code, and then BB Client can help Excel calculate these things without access to the
         knowledge base.

 - add a nice column that tracks all of the areas, show the area name in the merged cells there.
 - add a pretty cover sheet, with model name, "built by blackbird", legend if necessary
 - move to a paradigm where it's easy to add (or subtract) units
   -- can leverage the taxonomy concept
   -- to add: contribute extra copies of the taxonomy somewhere
      --- or can may be do that in memory?
      --- or approximate calculations?? (by life)? Otherwise, might get too large of a spreadsheet
      --- could add

 - figure out how to deal with unit growth:
      --- if some units are inactive early and active later, need more rows, so everything shifts down on
          their parents


IOP:
  - figure out what to do with the position indexing to make it consistent?
   -- really have to watch out for adding absolute positions to the relative lookup (will create gaps)

 - !add grouping to LineChef

 - add a main interface
 - add formula name, original output, may be even the docstring from func to formula info. That way, we can
   quickly trace it. Also add format_error intercept into Chef itself. 
 
 -!! check that lines and units don't share xl data
 -!!! make sure drivers only add their DriverData when they are allowed to work on the item.
 - think about whether to make maturity and decline dynamic from percent maturity, etc.
   alternatively, could just make the formula look at the event itself; probably better.
   so life[age]/(events{maturity}-events{birth}) <--------- can do this later.
 - define copy behavior for unit.xl (should probably get zeroed out)
 - by default, should add params to the master column

 - !! APPLY Sheet style to all sheets?
 - consider moving all the LineChef routines to kwargs.

 - !!! move UnitChef._add_unit_params to run on add_items_to_area() 
   
 
 

PROBLEM:
 - Good excel prep is not totally compatible with speed optimization. End up doing work in cases where
   a unit is dead and could otherwise pass.

   Examples (formulas):
   1. monthly_from_annual_inflation

Have to write an explanation that references can only point to lines
"""
# Expected interface

class Workbook:
    def __init__(self):
        pass
    
    def create_sheet(name):
        """
        -> Worksheet
        """
        # Sample logic:
        
##        result = Worksheet(name)
##        result.parent = self
##        self._sheets[name] = result
##        
##        return result
        pass

    def __getitem__(self, name):
        """

        -> Worksheet
        """
        return self._sheets[name]

    def get_sheet_by_name(self, name):
        return self._sheets[name]

class Worksheet:

    def __init__(self, name):
        self.parent = None
        # Points to book
        
        self.title = name
        
    def cell(column, row):
        """
        -> returns Cell with column and row
        """
        pass

class Cell
    def __init__(self):
        self.parent = None
        # Points to sheet

        self.value = None
        # Raw value

    @property
    def coordinate(self):
        pass
        # Returns alphanumeric coordinates

    @property
    def row(self):
        pass
        # Returns integer row

    @property
    def column(self):
        pass
        # Returns alphabetical column

    def set_explicit_value(value, data_type=None):
        """
        Coerce type
        """
        self.value = value
        self._data_type = data_type
    

        


                
