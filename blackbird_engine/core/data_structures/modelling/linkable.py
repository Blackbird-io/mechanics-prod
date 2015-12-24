class Linkable:
    def __init__(self):
        self.past = None
        self.future = None

    @property
    def linked(self):
        # return bool

        result = False
        
        if self.source:
            result = True
            
        return result

    def link(self, source, recur=True):
        #abstract method
        pass
        #or can say
        ## self.past = source
        ## source.future = self

    def sever(self, source, recur=True):
        pass

    #when you extrapolate forward:
        #everything is good, sort of
        #can just do the link
    
    #when you extrapolate backward...
        # link ends up running in the opposite direction
        # can add logic so that you determine direction based on dates?
        # or can only link if period is after?

        # what i want:
            # to load a starting balance sheet at the beginning and for everyone to pick it up
            # down the line

            # to make a change at period 10 and for it to show in period 20
            
        # so i can just link prior to following always
        # and determine which is which based on self.period

        # dont want to overwrite if already there?
        
    # or, can say that link is always manual
    # so first, extrapolate all
    # then link
    # bu.link(recur=True)

#so algorithm:
          #1. extrapolate
          #2. time_line.link()
             #connects all periods in order
             #for content, gets company.link(recur=True):
                #connect financials
                #pass on down the chain
    
          #3. #then fill out
             #problem: drivers fill out old time periods too
             #but if its new = old + now, then not a problem
