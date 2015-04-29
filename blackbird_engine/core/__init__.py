



#imports
import os
import sys


#globals
__author__ = 'loren'

#IOP: Adding adapter for Engine paths that assume core is the root dir
sub_dir = r"blackbird_engine/core"
sub_dir = os.path.normpath(sub_dir)
full_path = os.path.abspath(sub_dir)
#abspath should control for system style (fwd vs back slash, etc.) differences
#
#adding docker-specific path
dock_path = r"opt/apps/django/blackbird_engine/core"
dock_path = os.path.normpath(dock_path)
#
sys.path.append(sub_dir)
sys.path.append(dock_path)
#
##sys.path.append(full_path)
#all core modules should now be able to reference each other as before
