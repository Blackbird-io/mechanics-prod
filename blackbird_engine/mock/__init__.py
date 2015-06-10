import decimal
import random

EndInterview = 'END_interview'

_mock_questions = [
    dict(
        question_id='business_name',
        topic_name='Mock',

        progress=10,
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
        question_id='some_email',
        topic_name='Mock',

        progress=15,
        short='Email',
        prompt='How can we reach you?',
        array_caption='What is your business email?',
        input_array=[
            dict(
                input_type='text',
                input_sub_type='email',
                shadow='youremail@example.com',
            )
        ],
        input_type='text',
        input_sub_type='email',
    ),
    dict(
        question_id='ice_cream',
        topic_name='Mock',

        progress=20,
        short='Ice Cream',
        prompt='Your Favorite Flavor',
        comment='Which flavors of ice cream do you like?',
        input_array=[
            dict(
                input_type='choice',
                main_caption='Pick your favorite:',
                shadow='Ice Cream Flavor',
                entries=['Chocolate', 'Vanilla', 'Mint', 'Rocky Road'],
                allow_other=True,
                multi=True
            )
        ],
        input_type='choice',
        transcribe=True
    ),
    dict(
        question_id='industry',
        topic_name='Mock',

        progress=30,
        short='Industry',
        prompt='What industry are you in?',
        comment='Which flavors of ice cream do you like?',
        input_array=[
            dict(
                input_type='choice',
                main_caption='Your industry',
                shadow='Choose Industry',
                entries=['Agriculture', 'Financial Services', 'Healthcare', 'Retail', 'Technology', 'Water Polo'],
                allow_other=True,
                multi=False
            )
        ],
        input_type='choice',
        transcribe=True
    ),
    dict(
        question_id='store',
        topic_name='Mock',

        progress=30,
        short='Store Maturity',
        prompt='How long does it take for each store to reach maturity?',
        input_array=[
            dict(
                input_type='choice',
                main_caption='Time for stores to reach maturity',
                entries=['0-6 mos', '7-12 mos', '12-18 mos', '18-24 mos', '24+ mos'],
            )
        ],
        input_type='choice',
        transcribe=True
    ),
    dict(
        question_id='check_some_stuff',
        topic_name='Mock',

        progress=40,
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
        question_id='would_you_rather',
        topic_name='Mock',

        progress=50,
        short='Preferences',
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
        question_id='numbers',
        topic_name='Mock',

        progress=55,
        short='Numbers',
        prompt='Some numerical questions',
        array_caption='Various numbers',
        input_array=[
            dict(
                input_type='number',
                r_min=5000,
                r_max=10000,
                r_steps=1000,
                main_caption='Some numbers',
                user_can_add=True
            ),
            dict(
                input_type='number',
                input_sub_type='currency',
                r_min=5000,
                r_max=10000,
                main_caption='Currency',
            ),
            dict(
                input_type='number',
                input_sub_type='percent',
                r_min=0,
                r_max=1,
                main_caption='Percent',
            ),
            dict(
                input_type='number',
                input_sub_type='days',
                r_min=0,
                r_max=100,
                main_caption='Days',
            ),
            dict(
                input_type='number',
                input_sub_type='weeks',
                r_min=0,
                r_max=100,
                main_caption='Weeks',
            ),
            dict(
                input_type='number',
                input_sub_type='months',
                r_min=0,
                r_max=100,
                main_caption='Months',
            ),
            dict(
                input_type='number',
                input_sub_type='years',
                r_min=0,
                r_max=100,
                main_caption='Years',
            ),
        ],
        input_type='number',
        transcribe=True
    ),
    dict(
        question_id='number_range',
        topic_name='Mock',

        progress=60,
        short='Salaries',
        prompt='Your employees\' salaries',
        comment='Give an idea of how much your employees are paid.',
        input_array=[
            dict(
                input_type='number-range',
                input_sub_type='currency',
                main_caption='Salary Range',
                shadow='Lowest Salary',
                shadow_2='Highest Salary',
                r_steps=1000
            )
        ],
        input_type='number-range',
        transcribe=False
    ),
    dict(
        question_id='dates',
        topic_name='Mock',

        progress=65,
        short='Important Dates',
        prompt='Provide some important dates',
        input_array=[
            dict(
                input_type='date',
                r_min='2014-01-01',
                r_max='2014-12-31',
                main_caption='A date in 2014',
                shadow='YYYY-MM-DD'
            ),
            dict(
                input_type='date',
                r_min='2015-01-01',
                r_max='2015-01-31',
                main_caption='Some dates in January 2015',
                shadow='YYYY-MM-DD',
                user_can_add=True
            ),
            dict(
                input_type='date',
                main_caption='Any dates',
                shadow='YYYY-MM-DD',
                user_can_add=True
            ),
        ],
        input_type='date',
        transcribe=True
    ),
    dict(
        question_id='date_range',
        topic_name='Mock',

        progress=70,
        short='Vacation',
        prompt='When did you go on vacation last year?',
        input_array=[
            dict(
                input_type='date-range',
                r_min='2014-01-01',
                r_max='2014-12-31',
                main_caption='Vacation date range',
                shadow='Vacation Start',
                shadow_2='Vacation End',
                user_can_add=True
            ),
        ],
        input_type='date-range',
        transcribe=True
    ),
    dict(
        question_id='times',
        topic_name='Mock',

        progress=75,
        short='Times of the day',
        prompt='What is you schedule like?',
        input_array=[
            dict(
                input_type='time',
                r_min='00:00:00',
                r_max='18:00:00',
                main_caption='When do you wake up?',
                shadow='HH:MM:SS'
            ),
            dict(
                input_type='time',
                main_caption='What times do you eat?',
                shadow='HH:MM:SS',
                user_can_add=True
            ),
            dict(
                input_type='time',
                r_min='12:00:00',
                r_max='23:59:59',
                main_caption='What time do you go to sleep?',
                shadow='HH:MM:SS',
            ),
        ],
        input_type='time',
        transcribe=False
    ),
    dict(
        question_id='time_range',
        topic_name='Mock',
        progress=80,
        short='Work hours',
        prompt='When do you work?',
        input_array=[
            dict(
                input_type='time-range',
                shadow='Begin',
                shadow_2='End',
                user_can_add=True
            ),
        ],
        input_type='time-range',
        transcribe=True
    ),
    dict(
        question_id='business_name_2',
        topic_name='Mock',

        progress=85,
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
    dict(
        question_id='life_story',
        topic_name='Mock',

        progress=90,
        short='Life Story',
        prompt='Tell us your life story',
        comment='Take your time',
        input_array=[
            dict(
                input_type='text',
                shadow='Begin here',
                size='long',
                show_if=dict(
                    input_type='binary',
                    main_caption='Would you like to share yours?',
                ),
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
        self._m = dict(portal_model) if portal_model else dict()

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
