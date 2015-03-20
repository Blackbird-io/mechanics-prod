from django.conf.urls import url, include, patterns
from rest_framework import routers


def get_v0_patterns():
    from .views import EngineModelView

    router = routers.DefaultRouter()
    router.register(r'engine-model', EngineModelView)

    return patterns('',
                    url(r'', include(router.urls)),
                    )


urlpatterns = patterns('',
                       url(r'v0/', include(get_v0_patterns())),
                       )
'''
Endpoints:

Interview:

/interview(s)
    POST - create new interview, return (at least) id
    /{id}
        GET - current questions, each with ids/gets associated model & info ??
        POST - generate and return first question
        /question(s)
            /{sequence_id}
                GET - get just this question. necessary?
                POST - accepts a response
                     - deletes any questions with larger sequence_id
                     - create response and return next question OR redirect to model

        /stop
            POST - "stop" interview & redirect to model

/model(s)
    /{id}
        GET - get model info
        /landscape
            POST - get a new landscape summary
'''