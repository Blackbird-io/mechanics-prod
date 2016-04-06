class HistoryIterator:
    def __init__(self, snapshot):
        self.now = snapshot
        #should call this now

    def __next__(self):
        future = self.now.future
        if future is None:
            raise StopIteration
        else:
            self.now = future
            return future

class History:
    """

    Mix-in class for connecting objects across time. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    past                  pointer to the preceding version of the object
    future                pointer to the consequent version of the object
    
    FUNCTIONS:
    set_history()         set past to argument, recur if necessary
    ====================  ======================================================    
    """
    
    def __init__(self, recursive_attribute=None):
        self.past = None
        self.future = None
        self._recursive_attribute = recursive_attribute

    def set_history(self, history, clear_future=True, recur=True):
        """

        -> None
        ``history`` and instance should usually be two instances of the same
        class. If ``clear_future`` is True, method will set future on instance
        to None. Generally want to keep this setting when extrapolating forward
        on a timeline. You would want to set the argument to False if you are
        substituting the past while preserving linkages to the future, or if you
        are extrapolating backwards. 
        """
        self.past = history    
        history.future = self

        if clear_future:
            self.future=None        

        if recur:
        
            if self._recursive_attribute is not None:

                attr = getattr(self, self._recursive_attribute)
                attr_history = getattr(history, self._recursive_attribute)

                if attr:
                    attr.set_history(attr_history,  clear_future=clear_future, recur=True)

    def __iter__(self):
        return HistoryIterator(self)


        
