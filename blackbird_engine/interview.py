from . import models
from . import serializers

# TODO move this to engine api
END_SENTINEL = 'END'


def _send_engine_msg(bb_model, question=None, response=None):
    # TODO send data

    # mocking each model
    new_question_id = question['question_id'] + 1 if question else 0
    end = new_question_id >= 5
    model_dict = dict(e_model=dict())
    if end:
        model_dict['industry'] = 'Agriculture'
        model_dict['summary'] = {'is': 'awesome'}
        model_dict['business_name'] = 'Bob\'s Bakery'
        model_dict['tags'] = ['business', 'good', 'delicious', 'wow']
    question_dict = None if end else dict(question_id=new_question_id, prompt='Question ' + str(new_question_id))
    engine_end = END_SENTINEL if end else None

    return model_dict, question_dict, engine_end


def _get_question_dict(question=None):
    return question.detail if question else None


def _get_response_dict(question=None, end=False):
    return END_SENTINEL if end else _get_question_dict(question)


def _get_bb_model_dict(bb_model):
    return serializers.InternalBlackbirdModelSerializer(bb_model).data


def _save_bb_model_dict(business, model_dict, end=False):
    model = models.BlackbirdModel(business=business, complete=end, **model_dict)
    model.save()
    return model


def _save_question_dict(business, answered_question, model, end, question_dict):
    # TODO move to Question model
    sequence_num = answered_question.sequence_num + 1 if answered_question else 0
    question = None if end else models.Question.objects.create(business=business,
                                                               blackbird_model=model,
                                                               sequence_num=sequence_num,
                                                               **{k: v for (k, v) in question_dict.items() if v !=
                                                                  None})
    return question


def _get_model(business, prev_question=None):
    if prev_question:
        return prev_question.blackbird_model
    else:
        # don't create the dummy model
        return models.BlackbirdModel(business=business)


def _engine_update(business, answered_question=None, end=False):
    prev_bb_model = _get_model(business, answered_question)
    answered_question_dict = _get_question_dict(answered_question)
    response = _get_response_dict(answered_question, end)
    prev_bb_model_dict = _get_bb_model_dict(prev_bb_model)
    model_dict, question_dict, engine_end = _send_engine_msg(prev_bb_model_dict,
                                                             answered_question_dict,
                                                             response)
    end = engine_end == END_SENTINEL
    model = _save_bb_model_dict(business, model_dict, end)
    question = _save_question_dict(business, answered_question, model, end, question_dict)
    return question


def get_next_question(business, prev_question=None):
    return _engine_update(business, prev_question)


def stop_interview(business, prev_question=None):
    return _engine_update(business, prev_question, end=True)