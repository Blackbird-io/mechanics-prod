#Excel converter class

import openpyxl as xlio

class BBWorkBook(xlio.WorkBook):

    def __init__(self):        
        xlio.WorkBook.__init__(self)
        # Should probably use composition here: ._native_book = xlio.WorkBook()?

    def create_sheet_with_lookups(self, *pargs, **kwargs):

        sheet = self.create_sheet(*pargs, **kwargs)
        sheet.row_lookup = dict()
        sheet.col_lookup = dict()
    
        return sheet

    # Add range-management features (ie, make sure no ranges overlap)
    # can add a bb_ranges attribute that's just a dictionary. Then
    # would add ranges there.

    def validate(self):
        pass
        # check that none of the ranges overlap
    
class AttributeRange:
    """
    A range of cells that describe a particular attribute. 

    All values should be relative to starting points, 0-indexed. For example,
    row_lookup = {"revenue":4} means that the revenue figure is in the 5th row
    from the start. If instance.starting_row == 3, revenue will be in row 7 (8th
    row from the top).

    Ranges cannot overlap...? 
    """
    #<---------------------- Replace this guy with a real range object?
    
    def __init__(self, starting_col=0, starting_row=0):

        self.starting_col = starting_col
        self.ending_col = None

        self.starting_row = starting_row
        self.ending_row = None
        
        self.row_lookup = dict()
        self.col_lookup = dict()

    def get_row(self, label):
        relative_position = self.row_lookup[label] 
        result = self.starting_row + relative_position
        return result

    def get_column(self, label):
        relative_position = self.col_lookup[label]
        result = self.starting_col + relative_position
        return result
        
    def update(self, source):
        self.row_lookup.update(source.row_lookup)
        self.col_lookup.update(source.col_lookup)

        # Update ending values
        if self.col_lookup:
            highest = max(self.col_lookup.values())
            self.ending_col = self.starting_col + highest

        if self.row_lookup:
            highest = max(self.row_lookup.values())
            self.ending_row = self.starting_row + highest        

    def validate(self):
        """
        Return True or error if endpoints dont match up
        """
        pass
            
class ExcelConverter:
    def convert(self, model):
        """
        Return excel model
        """
        pass
    
    def save(self, model, path):
        """
        Save model to path
        """
        pass

    def _make_cover_tab(self, model, book):
        pass

    def _make_scenarios_tab(self, model, book):
        pass

    def _make_time_line_tab(self, model, book):
        pass

    def _spread_unit(self, model, book):
        # should do so on last tab

        # algo:
          # first, spread all of the components
          # then connect the balance sheet
          # then consolidate
          # then derive

        pass

    def _spread_line(self):
        """

        Can integrate into line and the line handle recursion
        """
        pass
    
    def _spread_driver(self, driver, tab, column, row):
        # goal:
            # take all of the params for the driver
            # put them in rows
            # put a formula in subtotal row
            # repeat for all columns? #<----------------------------------------------------------could do this at the unit level?
                # could do at unit level to start, since all columns should be the same generally
                # but undermines premise of extrapolation
                # so could toggle: extrapolate or stretch
            
            # group

        # steps:
            ## formula needs to supply its own formula
            ## formula MUST NOT look for lines on its own? (like EBITDA does today)
                ## won't know what to do
                ## may be i should have a formula port
                ## formula needs to specify the vars it uses
                ## may need to have a formula prep routine
                    ## can confirm that results fit?

            ## make a params-to-cells table
                ## if driver has its own params,
                    # add appropriate rows
                    # DONT put these in the lookup table; they are private

                ## or could be super explicit
                    # each driver always duplicates a row when it uses a shared param
                    # then overwrites some of these params on their own rows for driver-specific data

            ## make a driver subtotal line
                ## contains formula, generates the value you would get after the driver

            ## need a beginning value line
                ## so always have a starting value
                ## and ending value

            ## adjust the lookup table to point to the ending value as the row for that item
                ## 

            ## group

            ## add a clean final result
            
                ## at the end of derivation, the line should have a bunch of subtotals that are hidden
                ## and then a nice clean line underneath
                ## so this should be the final step


    def _spread_line(self):
        # challenge with lines is that they are recursive
        # i could do something like _get_ordered() and just list them in order
        # want to keep the auto-summation

        # for details in line.get_ordered():
            # spread basic line

        # then have to sum them
            # so cant really do full recursion
            # have to do just the elements here

        # general algo:
            # if you dont have details:
                # do the simple line derive

            # if you do have details:
                # fro each detail, do a line derive
                # create a table of final values for each detail
                # sum all of those values

    def _spread_unit_outline(self):
        # need to have a routine for consolidation
            # can just be a single line that sums results from other units
        # only comes in when you have components
            # so first spread all of them
            # then add them up
            # challenge:
                # what to do when you have lots and lots of components
                # end up with very long formulas
                # is that a problem per se?
                    # could do something in vba:
                        #if parent:
                            #consolidate into parent
                        #else:
                            #blah

        # need to have a line for derivation
        
        # steps:
            #make a derivation routine
            #make a consolidation routine

        # move to a general ledger
            # then balance sheet consolidation would be easier:
                # start with starting balance sheet
                # increment ending balance sheet by all of the child entries

    def _spread_unit(self, unit, book):
        children = unit.components.get_ordered()
        if children:
            # complex routine
            pass
        else:
            # simple routine

    def _spread_childless_unit(self, unit, book):
        """
        # create a tab for the unit
            # tab should be named same as unit? or same as unit id?
            # let's say id, that's guaranteed to be unique

        # add timeline info to that tab
            # link to timeline dates
            # link to timeline params

        # add unit-level params
            # overwrite timeline parameters
            # [should be in different color]

        # [add life]

        # [add relationships]
        
        # add financials

        housekeeping:
          return book
          active tab should be where you made the unit
          
        """
        sheet = book.create_sheet(unit.id.bbid)

        sheet.row_sections = Statement()
        # or could have segments 
        sheet.col_sections = Statement()

        

        # Can add a profile section here: name (or at the top)

        # Should configure each unit sheet with sections: timeline, parameters, life, financials

            # Could even add components: a list of all component ids in that period
            # Could then do consolidation through an actual routine in VBA:

                # for each unit id, find the tab, find the line, etc.
                # works better with named ranges <--------------------------------------------------------------------------

                # in the meantime, can just have a row_sections and col_sections dictionary
                # can make this a statement so they nest
                
        self._link_to_timeline(sheet)
        # <---------------------------------------------- implement

        self._add_unit_params(sheet, unit.params, column)
        # <---------------------------------------------- implement

    def _build_unit_sheet(self, book, unit):
        """
        -> sheet
        """

        sheet = book.create_sheet(unit.id.bbid)
        sheet.time_line = Range(self.TL_STARTING_ROW, self.TL_STARTING_COL)
        self._link_to_time_line(sheet, book)

        sheet.parameters = Range()
        # Populate the unit params

        sheet.life = Range()
        # Populate unit life (could be events?)        
                
        return sheet
           
            # Each section should have a starting_, ending_, and elements
                # lo and hi?
            # elements should be a Statement() and should nest (?)
                # nesting may not be useful, because then cant see top-down
                # but you do want to be able to find cells in a given range:
                    # search for assets in ending balance sheet
                    # search for cash in starting balance sheet

            # point is, you need structure
                # some structure is driven by sheet-level setup
                # some structure is driven by object characteristics
                    # for now, i can make the unit-tracking sheet manually
                    # ideally though, it should be a function of the unit itself
                        # so unit could pick out the attributes that get their own sections
                        # and each attribute could write itself, sort of

            # so its almost like:
                # create_sheet:
                    # sheet has certain attributes, like sections
                    # could have "general" key

                # add_timeline:
                    # adds other attributes to the sheet; new sections

                # add_unit_info:
                    # adds a whole swath of other data to the sheet

                    # what if each object had it's own xl_map attribute
                    # would contain rows
                    # would need to make sure rows appear only once
                    # would need to make sure it doesnt overlap with others
        # \\
        # Could have individual classes for different kinds of tabs
        # UnitSheet(unit) -> sheet with all of the stuff, standard offsets, etc.
        # but not that great; similar to a function, and may need multiple sheets (ie a book)
        
    def _old_link_to_timeline(self, sheet, book):

        tl_sheet = book[self.SHEET_NAME_TIME_LINE]
        # Timeline has columns with info. The first column is the index. Others
        # are periods. We want to copy the index and the periods. We can't iterate
        # over cells because that creates them in memory.

        # This is an element we should definitely fix in pandas <--------------------------------------------------------------------------------
        linking_formula = "{sheet_name}!{column}{row}"
        linking_formula.format(
            {
                "sheet_name" : tl_sheet.name
             }
            )

        # Use 3.x string formatting for more explicit syntax
        # formulas can be constant at class or module level    <-------------------------------------------------------------------------------------

        # Step 1: we start with the index column. Link cells in our sheet to those
        # cells. The cells there should contain strings that point to a parameter.

        for source_row in source.time_line.row_lookup:

            for source_column in source.time_line.col_lookup:

                local_row = my_sheet.time_line.starting_row + source_row
                local_col = my_sheet.time_line.starting_col + source_col
                # We could have all of the Range references in relative numbers
                # and then have a starting line. So values in the lookups would always start
                # at 0, and we would write to .starting + value
                # ending = .starting + max(lookup_vals)
                # validate?
                # could then run update operations too
                # <-----------------------------------------------------------------------------------------------good idea

                local_cell = my_tab.get_cell(local_column, local_row)
                
                local_cell.value = linking_formula.format(column, row)
                # Populate my_tab's tables with the right info

    def _link_to_time_line(self, sheet, book):
        source = book[TL_NAME]

        sheet.time_line.update(source.time_line)

        for row in source.time_line.row_lookup.values():

            source_row = source.time_line.starting_row + row
            local_row = sheet.time_line.starting_row + row

            for column in source.time_line.column_lookup.values():

                source_col = source.time_line.starting_col + column
                local_col = local.time_line.starting_col + column 

                cell = local.get_cell(local_col, local_row)
                cell.value = formula.format(source_col, source_row)


    def _link_to_period_parameters(self, sheet, book):

        source = book[TL_NAME]

        sheet.parameters.update(source.parameters)

        for row in source.parameters.row_lookup.values():
            # can be sorted if necessary

            source_row = source.parameters.starting_row + row
            local_row = sheet.parameters.starting_row + row

            for column in sheet.time_line.col_lookup.values():

                source_col = source.time_line.starting + column
                local_col = local.time_line.starting + column

                cell = local.get_cell(local_col, local_row)
                formula = link_to_cell.format(source_col, source_row)
                cell.value = formula

        # may want to group this stuff

    def _add_unit_parameters(self, sheet, unit, column):
        """
        add to active sheet?
        """
        #<-------------------------------------should have a current_period_column attribute on my sheets

        if active_column is None:
            active_column = sheet.time_line.current_period_column
            # or could do get_current() and mathc unit.period.ends to known
            # columns in timeline. probably better
                        
        ordered_params = sorted(unit.parameters.items(), key = lambda x: x[0])
        # Sort parameters so they appear in constant order

        for parameter_name, parameter_value in ordered_params:

            parameter_row = None
            existing_row = local.parameters.row_lookup.get(parameter_name)

            if existing_row:
                parameter_row = local.parameters.get_row(parameter_name)               

            else:
                parameter_row = sheet.parameters.ending_row + 1
                # write the param name to the index column 
            
            cell = local.get_cell(current_column, parameter_row)
            cell.value = parameter_value
            
            # add formatting
            # cell.format(local_data_in_blue)

        return local

    def _add_unit_life(self, sheet, unit, column):

        sheet.life = AttributeRange()
        # should start where Params end + 2
        # walk through events in order of keys
        # add each event to the section
        # check if event is already in section, if not, add

        # later, this can link to templates

    def _add_financials(self, sheet, unit, column):

        # go down every line
        # go through
            # formulas should deliver xl_formula inputs as range, something, something
            # basically need to map attributes to ranges
            #
            # if you have a very complex calculation (ie, sort units by some feature and tag, then do x and y to them),
            # may want to just enter the answer to that with a memo about the code (logic)
            #
            # or could just enter the value as fixed with an explanation (and comment like "Use blackbird!")
            #
            #
            # or could require a local runtime for some of these things, in which case can actually route through
            # the python routine?

            
            #
            # could i have the formulas map themselves?
                # driver.spread()
                    #spreads the parameters
                    #then 
                # give them a sheet
                # 
            # 
            
        
        # Step 2: we link the periodic values.

        # To link:
            # Need a formula        

        # go by column in tl_sheet
        # 
        # copy each period heading
        # copy each period params
        #
        # on sheet, need to populate lookup tables too
        
        ## may be i could do this with a named range?? but doesnt do too much good
        ##

    # also need to connect balance sheets (time-based ops)
    def _driver_spread(self):
        # spread the parameters
            # ! already have the params_to_inputs dictionary
            # basically go through that
                # add the input line
                # link the input line to a parameter
                    # first to shared ones
                    # second overlay local ones

                    # should look like:
                        # cows:     "=d14"
                        # bulls:    "=d18"
                        # chickens: "8" {source then overwrite}
                        # etc:      "8"
                        #
                        # subtotal: "A1 * A2 + A4"

            # hold its own map in memory?
                # can use a Range() but just not put it on the sheet
            # 
                    
        # add the formula
            # need to quickly map the attribute structure

        # group the lines
        
        # change the row value and run _update_endpoints()
        
    # notes on consolidate:
        # for the purposes of excel, can set parent to sum of children
            #and not worry so much about showing child-level detail

        # Alternatively:

        # for every line in child spread:
            ## since we spread the child, its flat, not recursive
            ## 
        
            # if line is already in parent
                # add to line

            # else:
                # copy line
            
        # for child in children:
            # for line in child.financials:
                ## child.financials is now flat

                # if line_name in parent.financials:
                    #

        ## conceptually:
            # for every line, make a list of units where it exists and the locations of the value
            # then go through that list and add a formula to the consolidated cell of parent that adds all of the children
                # try it on 5 stores

            # may be able to assume that lines dont change from period to period...

            # may be can replace ugly formula with cleaner Excel logic
                # or could spread vertically!!!!!! <--------------------------------------------------------------------------------EUREKA!
                # for every child, take their value
                    # copy it to a cell
                    # then sum all of those cells
                    # to get the consolidated value!!!!

                # will make for very long spreadsheets, but whatever
                    # problem is that you have to repeat for every line
                    # have to make sure you group

                    # can toggle format (consolidate_in_line = False)
                        # if consolidate_in_line=True, use long formulas
                        # otherwise, go by row
                        # can even toggle number of references: ie consolidate every 5 units into a cell, every 10
                            # number of units per cell is the control                        

                # can simplify the spreadsheets by adding templates and explicit links between the templates and everything else
                
                # and can then do the derive elements

        ##

        # consolidate: one range
        # derive: a second range
        # finals: a third range

        # add columns 1,2,3... that show ranges
            # specify them
    
        
        # 
        ##         

    def _spread_parent_unit(self, unit, book):
        pass

        # should populate relationships
    
    def _spread_driver_outline(self):
        """

        -> None

        column: point to column where we are doing this
        row: point to row where we starting writing

        options: can write to full tab, from start to end?
          probably should
          all in the same row

        let's start by writing column by column

        steps:
        1. if driver data:
          put driver data into rows, in order
            question: do we label these rows on the labels column?
            probably should

            #assemble driver-level row index that includes the driver-specific
            data, but DO NOT enter that data into the main sheet-level look-up
            table. that data is for the driver only. 

        2. convert formula to run on rows
            formula needs to return (i) a string with formula, and (ii) a
            list of all the fields

            if conversion logic cannot locate a field, should raise
            error

        3.  write the formula into a subtotal row
            #if the formula increments or changes a prior subtotal row, need to
            find it
            #can keep overwriting the subtotal for the line
              #so by default subtotal is zero
              #then we add subtotals, but "subtotal" always points to the last
              #row only

              #
        4. group the drivers into their own little thing
            #

        5. [Line level]:
            # header should be smtg like "{name} analysis:". header should be
            # grouped with all of the drivers and hidden.

        6. [Line level]: a little bit of a pain with details
            # can change the derive() algo to go through lines detail by detail, recursively
            # then can add the lines incrementally?
            # challenge: it is hard to insert rows and columns in openpyxl
               #check if that's the case
               #create methods if necessary: insert_rows(), insert_columns()

            # need to start with consolidate() though
              so line algo would be:
                 # go through line by line
                 # for each line:
                    # add a consolidation row
                    # then add driver details
                    # if at the conclusion of work row val doesnt equal bb val, raise error
                      # (but hard to do that, because won't evaluate formulas)
                      # (check how that works)
                 

        """
        pass

    
        

    
    
