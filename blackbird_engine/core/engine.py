from .mock import MockEngine

EndInterview = 'END_interview'


class Engine(MockEngine):
    def process_interview(self, portal_msg):
        return super(Engine, self).process_interview(portal_msg)

    def get_forecast(self, portal_model, fixed, ask):
        return super(Engine, self).get_forecast(portal_model, fixed, ask)

    def get_landscape_summary(self, portal_model):
        return super(Engine, self).get_landscape_summary(portal_model)
