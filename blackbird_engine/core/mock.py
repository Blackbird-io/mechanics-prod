EndInterview = 'END_interview'

_mock_questions = [
    dict(
        e_question=dict(),
        question_id='business_name',
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

# simplistic model for a linear interview
class EngineModel:
    def __init__(self, portal_model):
        self._m = dict(portal_model)

    @staticmethod
    def _base_e_model():
        return dict(q_idx=0)

    def _get_e_model(self):
        if not self._m['e_model']:
            self._m['e_model'] = dict(q_idx=0)
        return self._m['e_model']

    def complete(self):
        self._finalize()

    def update(self, question, response):
        if question['question_id'] == 'business_name':
            self._m['business_name'] = response[0]['response']
        elif question['question_id'] == 'industry':
            self._m['industry'] = response[0]['response']
        self._increment_q_idx()

    def get_next_question(self):
        idx = self._q_idx
        try:
            return _mock_questions[idx]
        except IndexError:
            return None

    @property
    def portal_model(self):
        return self._m

    @property
    def _q_idx(self):
        return self._get_e_model()['q_idx']

    @_q_idx.setter
    def _q_idx(self, q_idx):
        self._get_e_model()['q_idx'] = q_idx

    def _increment_q_idx(self):
        self._q_idx += 1
        if self._q_idx >= len(_mock_questions):
            self._finalize()

    def _finalize(self):
        self._m.setdefault('industry', 'Unknown')
        self._m.setdefault('summary', {'is': 'awesome', 'has': 10000000, 'needs': 20000000})
        self._m.setdefault('business_name', 'Unknown')
        self._m.setdefault('tags', ['incomplete-interview'])


class Message:
    def __init__(self, portal_msg):
        self._msg = portal_msg
        self._m = EngineModel(self._msg['M'])

    @property
    def portal_msg(self):
        self._msg['M'] = self._m.portal_model
        return self._msg

    @property
    def m(self):
        return self._m

    @property
    def q(self):
        return self._msg['Q']

    @q.setter
    def q(self, q):
        self._msg['Q'] = q

    @property
    def r(self):
        return self._msg['R']

    @r.setter
    def r(self, r):
        self._msg['R'] = r


class MockEngine:
    def process_interview(self, portal_msg):
        msg = Message(portal_msg)
        if msg.q:
            self._handle_response(msg.m, msg.q, msg.r)
        msg.q = self._get_next_question(msg.m)
        msg.r = None if msg.q else EndInterview
        return msg.portal_msg

    @staticmethod
    def _handle_response(m, q, r):
        if r == EndInterview:
            # complete model
            m.mark_complete()
        else:
            # updates model based on question/response
            m.update(q, r)

    @staticmethod
    def _get_next_question(m):
        return m.get_next_question()


    def get_forecast(self, portal_model, fixed, ask):
        # TODO
        pass

    def get_landscape_summary(self, portal_model):
        # TODO
        pass
