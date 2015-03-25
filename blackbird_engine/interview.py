from . import models
from . import serializers

# TODO move this to engine api
END_SENTINEL = 'END'


def _send_engine_msg(bb_model, question=None, response=None):
    # TODO send data

    # mocking each model
    try:
        question_num = bb_model['e_model']['question_num'] + 1
    except KeyError:
        question_num = 0
    end = question_num >= 5
    model_dict = dict(bb_model, e_model=dict(question_num=question_num))
    if end:
        model_dict['industry'] = 'Agriculture'
        model_dict['summary'] = {'is': 'awesome'}
        model_dict['business_name'] = 'Bob\'s Bakery'
        model_dict['tags'] = ['business', 'good', 'delicious', 'wow']
    question_dict = None if end else dict(question_id=str(question_num), prompt='Question ' + str(question_num))
    engine_end = END_SENTINEL if end else None

    return model_dict, question_dict, engine_end


def _strip_nones(dict):
    return {k: v for k, v in dict.items() if v is not None}


def _get_response_dict(question, end=False):
    return END_SENTINEL if end else question.response_array


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
    end = engine_end == END_SENTINEL
    model = _save_bb_model_dict(business, model_dict, end)
    question = _save_question_dict(business, answered_question, model, end, question_dict)
    return question


def get_next_question(business, prev_question=None):
    return _engine_update(business, prev_question)


def stop_interview(business, prev_question=None):
    return _engine_update(business, prev_question, end=True)