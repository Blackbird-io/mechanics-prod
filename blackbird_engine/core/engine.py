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


class Engine:
    def process_interview(self, portal_msg):
        model = portal_msg['M']
        question = portal_msg['Q']
        response = portal_msg['R']
        #TODO
        pass

    def get_forecast(self, portal_model, fixed, ask):
        #TODO
        pass

    def get_landscape_summary(self, portal_model):
        #TODO
        pass