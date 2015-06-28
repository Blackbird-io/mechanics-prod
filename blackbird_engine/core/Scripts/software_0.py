#Asnwer Script: software_0

answers = dict()
q1 = "company name?"
q2 = "company industry?"
q3 = "user name?"
q4 = "user position?"
q5 = "company start date?"
q6 = "subscription term in months?"
q7 = "subscriber life range?"
q8 = "subscriber count?"
q9 = "monthly subscription price?"
q10 = "employee head count across software company roles?"
q11 = "average annual salary across unspecified teams?"
q12 = "annual cash bonus as percent of salary for open teams?"
q13 = "annual stock bonus as percent of salary for open teams?"


#answer format: track api
#list is the PortalResponse object; dictionary is the ResponseElement object;
#user input in ResponseElement["response"]

answers[q1] = [{"response" : "goog"}]
answers[q2] = [{"response" : "software"}]
answers[q3] = [{"response" : "Ilya"}]
answers[q4] = [{"response" : "CEO"}]
answers[q5] = [{"response" : "1998-05-01"}]
#company started in may 1998
answers[q6] = [{"response" : "12"}]
answers[q7] = [{"response" : "[24, 72]"}]
answers[q8] = [{"response" : "500"}]
answers[q9] = [{"response" : "4000"}]
answers[q10] = [{"response" : "8"},
                #8 developers
                {"response" : "7"},
                #7 sales people
                {"response" : "5"},
                #5 managers
                {"response" : "12"}]
                #12 people in all other roles (``everyone else``)
answers[q11] = [{"response" : "120000"},
                #$120,000/yr for developers
                {"response" : "80000"},
                #$80,000/yr for sales
                {"response" : "140000"},
                #$140,000/yr for managers
                {"response" : "60000"}]
                #$60,000/yr for everyone else
answers[q12] = [{"response" : "25"},
                #cash bonus equal to 25% of salary for developers
                {"response" : "100"},
                #cash bonus equal to 100% of salary for managers (who set their
                #own bonus policy)
                {"response" : "15"}]
                #cash bonus equal to 15% of salary for everyone else
                #
                #NOTE: this question should exclude the sales team
answers[q13] = [{"response" : "60"},
                #stock bonus equal to 60% of salary for developers
                {"response" : "30"},
                #stock bonus equal to 30% of salary for managers
                {"response" : "5"}]
                #stock bonus equal to 5% of salary for everyone else
                #
                #NOTE: this question should exclude the sales team
