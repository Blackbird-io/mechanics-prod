



#imports
import os
import sys


#globals
__author__ = 'loren'

#IOP: Adding adapter for Engine paths that assume core is the root dir
sub_dir = r"blackbird_engine/core"
full_path = os.path.abspath(sub_dir)
#abspath should control for system style (fwd vs back slash, etc.) differences
sys.path.append(full_path)
#all core modules should now be able to reference each other as before
