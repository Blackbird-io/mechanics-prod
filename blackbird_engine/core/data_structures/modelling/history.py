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

    def set_history(self, history, recur=True):
        """

        -> None
        ``history`` and instance should usually be two instances of the same
        class.
        """
        self.past = history
        history.future = self
        
        if self._recursive_attribute is not None:

            attr = getattr(self, self._recursive_attribute)
            attr_history = getattr(history, self._recursive_attribute)

            if attr:
                attr.set_history(attr_history, recur=True)



        
