"""
Module integrates Engine core into Enginer-Wrapper.
"""




# Imports
import Shell as Engine
from tools import for_messages as message_tools




# Constants
# n/a

# Other globals
Engine.low_error  = True
Engine.enable_web_mode()

EndInterview = message_tools.END_INTERVIEW

chop = Engine.chop
get_forecast = Engine.get_forecast
get_landscape_summary = Engine.get_landscape_summary
process_interview = Engine.process_interview
