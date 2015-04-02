import decimal
import random

EndInterview = 'END_interview'

_mock_questions = [
    dict(
        e_question=dict(),
        question_id='business_name',
        topic_name='Mock',

        progress=0.1,
        short='Name',
        prompt='Let\'s get Introduced',
        comment='Names are a great way to get acquainted. You know ours, now tell us yours.',
        array_caption='What is the name of your business?',
        input_array=[
            dict(
                input_type='text',
                input_sub_type=None,
                main_caption=None,
                shadow='Business Name',
                size=None,
                show_if=None,
                user_can_add=False
            )
        ],
        input_type='text',
        input_sub_type=None,
        transcribe=False
    ),
    dict(
        e_question=dict(),
        question_id='check_some_stuff',
        topic_name='Mock',

        progress=0.2,
        short='Check',
        prompt='Are these true?',
        array_caption='Check all that apply:',
        input_array=[
            dict(
                input_type='bool',
                line_value='Green',
                main_caption='Your favorite color',
            ),
            dict(
                input_type='bool',
                main_caption='You like to sing.',
            ),
            dict(
                input_type='bool',
                main_caption='The earth is round.',
            )
        ],
        input_type='bool',
        transcribe=True
    ),
    dict(
        e_question=dict(),
        question_id='would_you_rather',
        topic_name='Mock',

        progress=0.3,
        short='Check',
        prompt='Would you rather',
        array_caption='Which do you prefer:',
        input_array=[
            dict(
                input_type='binary',
                toggle_caption_true='Hot',
                toggle_caption_false='Cold',
                main_caption='Porridge',
            ),
            dict(
                input_type='binary',
                toggle_caption_true='Sun',
                toggle_caption_false='Rain',
                main_caption='Weather',
            ),
            dict(
                input_type='binary',
                toggle_caption_true='Star Trek',
                toggle_caption_false='Star Wars',
            ),
        ],
        input_type='binary',
        transcribe=True
    ),
    dict(
        e_question=dict(),
        question_id='business_name_2',
        topic_name='Mock',

        progress=0.9,
        short='Second Name',
        prompt='Let\'s get Introduced',
        comment=None,
        array_caption='What are some other names for your business?',
        input_array=[
            dict(
                input_type='text',
                input_sub_type=None,
                main_caption=None,
                shadow='2nd Business Name',
                size=None,
                show_if=None,
                user_can_add=True
            )
        ],
        input_type='text',
        input_sub_type=None,
        transcribe=False
    ),
]


def random_currency():
    num = random.randrange(1000000, 100000000, 1000000)
    return decimal.Decimal('{:d}.00'.format(num))


def random_percent():
    num = random.randrange(0, 1000000)
    return decimal.Decimal('0.{:06d}'.format(num))


def random_years():
    return random.uniform(1.0, 3.0)


def random_structure():
    return random.randrange(0, 10)


def get_landscape_summary():
    return dict(
        # borrower = borrower, #this line isn't necessary?
        size_lo=random_currency(),
        size_hi=random_currency(),
        price_lo=random_percent(),
        price_hi=random_percent(),
    )


def _get_random_credit_scenario(price=None, size=None):
    return dict(
        size=size if size else random_currency(),
        price=price if price else random_percent(),
        term=random_years(),
        value=random_percent(),
        structure=random_structure()
    )


def _get_forecast(price=None, size=None):
    assert price or size
    return dict(
        price=price,
        size=size,
        bad=_get_random_credit_scenario(price=price, size=size),
        mid=_get_random_credit_scenario(price=price, size=size),
        good=_get_random_credit_scenario(price=price, size=size),
    )


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
        self._q_idx = len(_mock_questions)

    def update(self, question, response):
        if question['question_id'] == 'business_name':
            self._m['business_name'] = response[0]['response'][0]
        elif question['question_id'] == 'industry':
            self._m['industry'] = response[0]['response'][0]
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
        defaults = {
            'industry': 'Unknown',
            'summary': {'is': 'awesome', 'has': 10000000, 'needs': 20000000},
            'business_name': 'Unknown',
            'tags': ['incomplete-interview'],
        }
        self._m.update({k: v for k, v in defaults.items() if not self._m[k]})


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
            m.complete()
        else:
            # updates model based on question/response
            m.update(q, r)

    @staticmethod
    def _get_next_question(m):
        return m.get_next_question()


    def get_forecast(self, portal_model, fixed, ask):
        portal_model['summary']['has'] += 1
        return portal_model, fixed, ask, _get_forecast(price=ask if fixed == 'price' else None,
                                                       size=ask if fixed == 'size' else None)

    def get_landscape_summary(self, portal_model):
        portal_model['summary']['needs'] += 1
        return portal_model, get_landscape_summary()
