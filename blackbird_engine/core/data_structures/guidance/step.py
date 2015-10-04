#module provides shared core for valuation objects. valuation objects generally
#are data containers with a fixed structure. 




#imports
import tools.for_printing as printing_tools

from data_structures.guidance.guide import Guide
from data_structures.system.print_as_line import PrintAsLine
from data_structures.system.tags import Tags




#globals
#n/a

#classes
class Step(Tags, PrintAsLine):
    def __init__(self, name = None, priority = None, quality = None):
        Tags.__init__(self)
        PrintAsLine.__init__(self)
        self.guide = Guide(priority, quality)
        self.setName(name)
        
    def pre_format(self, **kargs):
        #custom formatting logic
        if self.name:
            kargs["name"] = self.name
        self.formatted = printing_tools.format_completed(self, **kargs)
        
        



    
