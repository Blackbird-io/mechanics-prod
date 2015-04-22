from django.apps import AppConfig

from . import signals


class BlackbirdEngineConfig(AppConfig):
    name = 'blackbird_engine'
    verbose_name = "Blackbird Engine"

    def ready(self):
        signals.register()