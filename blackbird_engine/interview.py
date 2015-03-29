from django.http import Http404

from . import models
from . import serializers
from .core.engine import EndInterview, Engine


def _send_engine_msg(bb_model, question=None, response=None):
    msg = Engine().process_interview(dict(M=bb_model, Q=question, R=response))
    return msg['M'], msg['Q'], msg['R']


def _strip_nones(d):
    return {k: v for k, v in d.items() if v is not None}


def _get_response_dict(question, end=False):
    return EndInterview if end else question.response_array


def _get_bb_model_dict(bb_model):
    return serializers.InternalBlackbirdModelSerializer(bb_model).data


def _save_bb_model_dict(business, model_dict, end=False):
    s = serializers.InternalBlackbirdModelSerializer(data=_strip_nones(model_dict))
    assert s.is_valid(), 'BlackbirdModel from Engine is valid'
    return s.save(business=business, complete=end)


def _get_question_dict(question):
    return serializers.InternalQuestionSerializer(question).data


def _save_question_dict(business, answered_question, model, end, question_dict):
    if end:
        return None
    else:
        # TODO move to Question manager?
        sequence_num = answered_question.sequence_num + 1 if answered_question else 0
        return models.Question.objects.create(business=business,
                                              blackbird_model=model,
                                              sequence_num=sequence_num,
                                              **_strip_nones(question_dict))


def _get_model(business, prev_question=None):
    if prev_question:
        return prev_question.blackbird_model
    else:
        # don't create the dummy model in db
        return models.BlackbirdModel(business=business)


def _engine_update(business, answered_question=None, end=False):
    prev_bb_model = _get_model(business, answered_question)
    prev_bb_model_dict = _get_bb_model_dict(prev_bb_model)
    if answered_question:
        answered_question_dict = _get_question_dict(answered_question)
        response_dict = _get_response_dict(answered_question, end)
        engine_msg = _send_engine_msg(prev_bb_model_dict, answered_question_dict, response_dict)
    else:
        engine_msg = _send_engine_msg(prev_bb_model_dict)
    model_dict, question_dict, engine_end = engine_msg
    assert model_dict and (question_dict or engine_end), 'Message from Engine is valid'
    end = engine_end == EndInterview
    model = _save_bb_model_dict(business, model_dict, end)
    question = _save_question_dict(business, answered_question, model, end, question_dict)
    return question


def get_next_question(business, prev_question=None):
    return _engine_update(business, prev_question)


def stop_interview(business, prev_question=None):
    return _engine_update(business, prev_question, end=True)


def get_landscape_summary(business):
    if not business.current_model.complete:
        raise Http404()
    prev_bb_model_dict = _get_bb_model_dict(business.current_model)
    model_dict, landscape_summary = Engine().get_landscape_summary(prev_bb_model_dict)
    _save_bb_model_dict(business, model_dict, end=True)
    return landscape_summary


def get_forecast(business, price=None, size=None):
    if not business.current_model.complete:
        raise Http404()
    prev_bb_model_dict = _get_bb_model_dict(business.current_model)
    fixed = 'price' if price else 'size'
    ask = price if price else size
    model_dict, fixed_out, ask_out, forecast = Engine().get_forecast(prev_bb_model_dict, fixed, ask)
    _save_bb_model_dict(business, model_dict, end=True)
    return forecast

