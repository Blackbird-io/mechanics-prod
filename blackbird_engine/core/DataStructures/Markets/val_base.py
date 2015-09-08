#module provides shared core for valuation objects. valuation objects generally
#are data containers with a fixed structure. 



#imports
import Tools.for_printing as printing_tools

from DataStructures.Guidance.Guide import Guide
from DataStructures.Platform.print_as_line import PrintAsLine
from DataStructures.Platform.Tags import Tags


#globals
#n/a

#classes
class ValBase(Tags, PrintAsLine):
    def __init__(self, name = None):
        Tags.__init__(self)
        PrintAsLine.__init__(self)
        self.guide = Guide()
        self.setName(name)
        
    def pre_format(self, **kargs):
        #custom formatting logic
        if self.name:
            kargs["name"] = self.name
        self.formatted = printing_tools.format_completed(self, **kargs)
        
        



    
