#new_statement

class Statement:
    def __init__(self):
        self.contents = dict()
        self.position = set()
        #tracks known positions
        
    def __getitem__(self, index):
        pass
        # no recursion here

    def __eq__(self):
        #true if all the lines compare True
        pass
        
    @property
    def max_position(self):
        #return max of self.positions
        pass
    
    def positions(self):
        pass
        #go through all items, collect positions
        
    def __setitem__():
        pass

    def _add_item(self, item, position, overwrite=False):
        if position in self.positions:
            raise Error
        else:
            self.contents[item.name] = item
        
    def add_top_line(self, line):
        #pass

    def add_line_to(self, line, tree):
        #step through tree and delegate to the right content
        
    def append(self, item):
        # add item at lowest possible position above the maximum
        pass

    def copy(self):
        pass
        #specialized copy rules

    def update(self):
        pass

class NewLine(Statement):
    """
    """
    #should leverage the Statement extrapolation and copying rules
    #only real difference
    
    def __init__(self):
        Statement.__init__(self)
        self._value = None
        self.signatures = []
        #

    @property
    def value
        #should return sum of all contents
        #or _value + sum of all contents
        #if _value is specified and there are details, drop the thing, then return all the details
        if self.details and self._value:
            replica = NewLine()
            replica.set_value(self.value)
            #check for replicas, increment if necessary
            self.add_item(replica)
            self.set_value(None)

        total = sum(self.details, lambda x : x.value)
        return total
    
    def set_value(self, value, signature):
        #should add a Line to contents with the value that we want
        #that's infinitely recursive unfortunately
        #could manually set the _value on the inner element...
        #... but only if you have details
        #so if you have details and you set the value, then add in a little one        
        pass

        #write normally here

    def setValue(**kwargs):
        pass
        #delegate to set_value

    
    

    

    

    
        

    
