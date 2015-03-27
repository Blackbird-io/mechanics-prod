_mock_questions = [
    dict(
        e_question=dict(),
        question_id='ABCDE',
        topic_name='Mock',

        progress=0.0,
        short='Name',
        prompt='Let\'s get Introduced',
        comment='Names are a great way to get acquainted. You know ours, now tell us yours.',
        array_caption='What is the name of your business?',
        input_array=[
            dict(
                input_type='text',
                input_sub_type=None,
                main_caption=None,
                response=None,  # TODO should this be here?
                shadow='Business Name',
                size=None,
                show_if=None
            )
        ],
        input_type='text',
        input_sub_type=None,
        # user_can_add=False, #TODO where will this live?
        transcribe=False
    )
]

EndInterview = 'END_interview'


class _Message:
    def __init__(self, portal_msg):
        self._msg = portal_msg

    @property
    def m(self):
        return self._msg['M']

    @m.setter
    def set_m(self, m):
        self._msg['M'] = m

    @property
    def q(self):
        return self._msg['M']

    @q.setter
    def set_q(self, q):
        self._msg['Q'] = q

    @property
    def r(self):
        return self._msg['R']

    @r.setter
    def set_r(self, r):
        self._msg['R'] = r

    @property
    def portal_msg(self):
        return self._msg


class _EngineModel:
    def __init__(self, portal_model):
        self._m = portal_model

    def _get_e_model(self):
        if 'e_model' not in self._m:
            self._m['e_model'] = dict()
        return self._m['e_model']

    @property
    def q_idx(self):
        # TODO
        pass

class Engine:
    def process_interview(self, portal_msg):
        msg = _Message(portal_msg)

        if msg.q:
            assert 'e_model' in msg.m, 'Model properly configured'
            msg.m = self._handle_response(msg)
        else:
            # creates model
            msg.m = self._init_interview(msg)
        msg.q = self._get_next_question(msg)
        msg.r = None if msg.q else EndInterview
        return msg.portal_msg

    def _handle_response(self, msg):
        if msg.r == EndInterview:
            msg.q = None
        else:
            # updates model based on question/response
            msg.m = self._update_model(msg)
        # TODO
        return msg.m
        pass

    def _init_interview(self, msg):
        m = dict(msg.m)
        m['e_model'] = dict(q_idx=0)
        return m

    def _get_next_question(self, msg):
        m = msg.m
        q_idx =
        q = _mock_questions[m['e_model']['q_idx']]


    def get_forecast(self, portal_model, fixed, ask):
        # TODO
        pass

    def get_landscape_summary(self, portal_model):
        # TODO
        pass

    '''

    try:
        question_num = bb_model['e_model']['question_num'] + 1
    except (KeyError, TypeError):
        question_num = 0
    end = question_num >= 5
    model_dict = dict(bb_model, e_model=dict(question_num=question_num))
    if end:
        model_dict['industry'] = 'Agriculture'
        model_dict['summary'] = {'is': 'awesome'}
        model_dict['business_name'] = 'Bob\'s Bakery'
        model_dict['tags'] = ['business', 'best', 'delicious', 'wow']
    question_dict = None if end else dict(question_id=str(question_num), prompt='Question ' + str(question_num))
    engine_end = END_SENTINEL if end else None
    '''
