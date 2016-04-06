#_new_line

from ._new_statement import Statement

class Line(Statement):
    """

    A statement with value and position

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    position
    value
    
    FUNCTIONS:

    ====================  ======================================================
    """
    def __init__(self, name=None, value=None, position=None):
        Statement.__init__(self, name)
        
        self._local_value = value
        self.position = position

    @property
    def value:
        #if details empty, return _local_value
        result = None
        if not self.details:
            result = self._local_value
        else:
            if self._local_value is not None:
                replica = self.details[self.name]
                new_value = replica.value + self._local_value
                replica.set_value(new_value)
                self._local_value = None

                #will have to insert replica if needed
                #should make this a subroutine: get_replica()

            result = self._total_detail_value()

        return result

    def __str__(self):
        if self.details:
            #print as statement plus own value
            #show header
            #show tabbed details
            #show result
            result = ""
            result += PrintAsLine.print_as_header(self)
            #this part will need to be tabbed correctly
            result += Statement.__str__(self)
            #print the details, as in statement; need to tab
            result += PrintAsLine.print_total(self.value)
            #also needs to be tabbed
        else:
            result = PrintAsLine.__str__(self)
        return result

    def _get_replica(self):
        
        replica = self.details.get(self.name)
        if replica is None:
            new_replica = copy.copy(self)
            # Shallow copy
            new_replica.clear()
            # Get rid of details and any defined value
            replica = new_replica
    

        return replica
        
    def _total_detail_value(self):
        result = None

        for detail in self.details.values():
            
            if detail.value is not None:
                result = result or 0
                # If result is still None, move to 0 so we can perform addition
                result += detail.value

        return result

        # Have to make sure that a line with multiple details that have None values returns
        # a None value

    def set_value(self, value):
        self._local_value = value

    def clear(self):
        """
        -> None
        """
        self.set_value() #<--------------------------------set value to zero
        Statement.reset(self)

    def increment(self, line):
        #add line.value to your value
        #sign yourself with consolidated tag
        #then run Statement.increment(self, line) to take care of the details
        pass
        
