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



                
