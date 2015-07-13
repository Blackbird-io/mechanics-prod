#Asnwer Script: software_3
#just like software_1, except the company charges by subscriber. revenue per
#subscriber goes up to $12,000 to cover expenses. 

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
q14 = "net subscription revenues after commission?"
q15 = "ltm whole company marketing spend?"
q16 = "ltm whole company overhead, excluding marketing?"
q17 = "annual spend on development and design contractors?"
q18 = "average seats per subscriber?"
q19 = "monthly office expense for whole company?"
q20 = "software function?"
q21 = "software subscription or product?"
q22 = "do you charge subscribers by seat?"
##q23 = "total paying subscriber seats?"
##q24 = "monthly seat price?"
q25 = "monthly hosting spend for whole company?"

#answer format: track api
#list is the PortalResponse object; dictionary is the ResponseElement object;
#user input in ResponseElement["response"]

answers[q1] = [{"response" : "AIQ"}]
answers[q2] = [{"response" : "software"}]
answers[q3] = [{"response" : "Gary"}]
answers[q4] = [{"response" : "CFO, Founder"}]
answers[q5] = [{"response" : "2010-02-01"}]
#company started in may 1998
answers[q6] = [{"response" : "12"}]
answers[q7] = [{"response" : "[36, 72]"}]
answers[q8] = [{"response" : "1050"}]
                #1050 subscribers
answers[q9] = [{"response" : "750"}]
                #$12000/mo per subscriber
answers[q10] = [{"response" : "5"},
                #8 developers
                {"response" : "11"},
                #7 sales people
                {"response" : "2"},
                #5 managers
                {"response" : "16"}]
                #12 people in all other roles (``everyone else``)
answers[q11] = [{"response" : "125000"},
                #$120,000/yr for developers
                {"response" : "125000"},
                #$80,000/yr for sales
                {"response" : "180000"},
                #$140,000/yr for managers
                {"response" : "65000"}]
                #$60,000/yr for everyone else
answers[q12] = [{"response" : "0"},
                #cash bonus equal to 0% of salary for developers
                {"response" : "0"},
                #cash bonus equal to 0% of salary for managers (who set their
                #own bonus policy)
                {"response" : "0"}]
                #cash bonus equal to 0% of salary for everyone else
                #
                #NOTE: this question should exclude the sales team
answers[q13] = [{"response" : "0"},
                #stock bonus equal to 0% of salary for developers
                {"response" : "0"},
                #stock bonus equal to 0% of salary for managers
                {"response" : "0"}]
                #stock bonus equal to 0% of salary for everyone else
                #
                #NOTE: this question should exclude the sales team
answers[q14] = [{"response" : "0.88"}]
                #keep 95% of revenue, pay out 5% in commissions
answers[q15] = [{"response" : "325000"}]
                #$250,000 LTM marketing spend
answers[q16] = [{"response" : "240000"}]
                #$30,000 in g&a
answers[q17] = [{"response" : "300000"}]
                #$180,000 in annual spend on 3d party developers
answers[q19] = [{"response" : "20000"}]
                #$50,000 /month for office space for the company
answers[q20] = [{"response" : "We help mutual funds sell to wholesale."}]
answers[q21] = [{"response" : "subscription"}]
answers[q22] = [{"response" : "No (flat subscription fee)"}]
answers[q25] = [{"response" : "4000"}]
                #$3500 per month for hosting
    
