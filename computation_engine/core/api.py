def begin_model():
    """
    Initializes an empty partial model
    @return: C{(partial_model, question_id, question_params)}
        - C{partial_model} - partial model
        - C{question_id} - id of first question
        - C{question_params} - python dictionary of options for question
    @rtype: (object, int, {str:str})
    """
    pass


def update_model(partial_model, question_id, answer):
    """
    Updates a model based on answer to most recent question
    @param partial_model: partial model
    @type partial_model: object
    @param question_id: id of question being answered
    @type question_id: int
    @param answer: answer for question.  the type of this parameter depends on the question
    @type answer: Any
    @return: C{(model, question_id, question_params)}
        - C{model} - updated partial model, or a complete model if C{question_id is None}
        - C{question_id} - id of next question. C{None} if the model is complete.
        - C{question_params} - python dictionary of options for question. C{None} if the model is complete.
    @rtype: (object, int or None, {str:Any} or None)
    """
    pass


def summarize_model(model):
    """
    Provides a summary based on the model
    @param model: complete model
    @return: summary of complete model, e.g. C{{'yearly_revenue': 20000.0, 'cashflow':5000000.0,
    'enterprise_value':10000000.0, 'leverable_assets' : 1000000.0, 'borrow_cap' : 10000000.0, 'use_of_proceeds':
    750000.0}}
    @rtype: {str:float}
    """


def forecast_model(model, desired_type, desired_value):
    """
    Provides Blackbird Forecasting for given model
    @param model: complete model
    @type model: object
    @param desired_type: C{'capital'}, or C{'rate'}
    @type desired_type: str
    @param desired_value: user's desired capital amount or rate
    @type desired_value: int or float
    @return: a forecast C{{rating:summary}}
        - C{rating} - C{'best'}, C{'average'}, or C{'poor'}
        - C{summary} - forecast details, e.g. C{{'size':45000000.0, 'price':0.07375, 'term_months':36}}
    @rtype: {str, {str,number}}
    """
    pass


def reference_pricing(model):
    """
    Provides Blackbird Reference Pricing for given model
    @param model: complete model
    @type model: object
    @return: a reference pricing summary, e.g. C{{'amount':(5000000,50000000), 'rate':(0.06, 0.25)}}
    @rtype: {str, tuple}
    """