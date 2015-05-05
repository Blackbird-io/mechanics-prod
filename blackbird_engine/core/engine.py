




#imports
from . import BBGlobalVariables as Globals
from . import Shell as Engine




#globals
Engine.low_error  = True
Engine.enable_web_mode()

EndInterview = Globals.END_INTERVIEW

get_forecast = Engine.get_forecast
get_landscape_summary = Engine.get_landscape_summary
process_interview = Engine.process_interview

##from .mock import MockEngine
##
##EndInterview = 'END_interview'
##
##
##class Engine(MockEngine):
##    def process_interview(self, portal_msg):
##        return super(Engine, self).process_interview(portal_msg)
##
##    def get_forecast(self, portal_model, fixed, ask):
##        return super(Engine, self).get_forecast(portal_model, fixed, ask)
##
##    def get_landscape_summary(self, portal_model):
##        return super(Engine, self).get_landscape_summary(portal_model)
