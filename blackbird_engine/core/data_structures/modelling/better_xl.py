class XL2:

    def _spread_financials():

        # Expects each line to come with enough data
        # runs each of the steps with spread=True, book=blah to pick up data
        # then when everything is ready puts the data on the sheet
        
        pass
    

    def _spread_derived_line_data(self, line, sheet):

        label_column = sheet.time_line.by_name["labels"]

        for driver_data in line.xl.derived.drivers:

            private_range = sheet.parameters.copy()
            for row_data in driver_data.rows:

                param_cell = sheet.cell(sheet.current_column, sheet.current_row)
                param_cell.value = row_data["value"]

                label_cell = sheet.cell(label_column, sheet.current_row)
                label_cell.value = row_data["label"]

                private_range.rows.by_name[label_cell.value] = sheet.current_row

                sheet.current_row += 1

            # Now, transform the range values from rows to columns
            coordinate_range = Range()
            current_column = get_alpha(sheet.current_column)

            for k, v in private_range.rows.by_name.items():

                coordinate_range[k] = current_column + v

            # Now, apply the conversions as necessary to make sure formula
            # sees all the params it wants
            conversion_map = driver_data.conversion_map
            for param_name, var_name in conversion_map.items():

                coordinate_range[var_name] = coordinate_range[param_name]

            # Finally, format the formula as necessary
            # (if references are a dict of objects, could map each obj to its coordinates)\
            formula = driver_data.excel_formula
            # formula is a template string
            references = driver_data.object_references
            formula.format(references=references, parameters=coordinate_range)
            

            formula_cell = sheet.cell(sheet.current_column, sheet.current_row)
            formula_cell.value = formula

            # If formula included a reference to the prior value of the line itself, it
            # picked up here. Can now change line.xl.derived.final
            line.xl.rows.derived.final = sheet.current_row

            sheet.current_row += 1

            # Also need to mark the final position on the line. That means final derived
            # result will always be the one that the line has at run time. 

    def _spread_line(self, line):

        # spread the consolidated info
        # sum
        # spread the derived info
        # don't sum!
        # spread the details recursively
        # sum the details
        # sum all of the types of values

    
    
            

            

            

            


            

            

            
            

                

                
            

            

                
        

    
