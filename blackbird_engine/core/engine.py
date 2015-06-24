




#imports
from . import BBGlobalVariables as Globals
from . import Shell as Engine
from .. import mock as MockEngine



#globals
Engine.low_error  = True
Engine.enable_web_mode()

EndInterview = Globals.END_INTERVIEW

if True:
    get_forecast = Engine.get_forecast
    get_landscape_summary = Engine.get_landscape_summary
    process_interview = Engine.process_interview
else:
    get_forecast = MockEngine.get_forecast
    get_landscape_summary = MockEngine.get_landscape_summary
    process_interview = MockEngine.process_interview
