



#imports
import Tools.for_printing as printing_tools




#globals
#n/a

#classes
class ValBase(PrintAsLine):
    def __init__(self, name = None):
        self.guide = Guide()
        self.tags = Tags()
        self.tags.setName(name)
        
    def pre_format(self, **kargs):
        #custom formatting logic
        if self.tags.name:
            kargs["name"] = self.tags.name
        self.formatted = printing_tools.format_completed(self, **kargs)
        
        



    
