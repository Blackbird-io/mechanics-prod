#module provides shared core for valuation objects. valuation objects generally
#are data containers with a fixed structure. 



#imports
import Tools.for_printing as printing_tools

from DataStructures.Platform.print_as_line import PrintAsLine



#globals
#n/a

#classes
class ValBase(PrintAsLine):
    def __init__(self, name = None):
        PrintAsLine.__init__(self)
        self.guide = Guide()
        self.tags = Tags()
        self.tags.setName(name)
        
    def pre_format(self, **kargs):
        #custom formatting logic
        if self.tags.name:
            kargs["name"] = self.tags.name
        self.formatted = printing_tools.format_completed(self, **kargs)
        
        



    
