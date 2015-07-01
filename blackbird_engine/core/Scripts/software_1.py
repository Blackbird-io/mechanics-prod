#Asnwer Script: software_1

answers = dict()
q1 = "company name?"
q2 = "company industry?"
q3 = "user name?"
q4 = "user position?"
q5 = "company start date?"
q6 = "subscription term in months?"
q7 = "subscriber life range?"
q8 = "subscriber count?"
##q9 = "monthly subscription price?"
####script designed for seat-sensitive companies
q10 = "employee head count across software company roles?"
q11 = "average annual salary across unspecified teams?"
q12 = "annual cash bonus as percent of salary for open teams?"
q13 = "annual stock bonus as percent of salary for open teams?"
q14 = "net subscription revenues after commission?"
q15 = "ltm whole company marketing spend?"
q16 = "ltm whole company overhead, excluding marketing?"
q17 = "annual spend on development and design contractors?"
##q18 = "average seats per subscriber?"
####script designed for seat-sensitive companies
q19 = "monthly office expense for whole company?"
q20 = "software function?"
q21 = "software subscription or product?"
q22 = "do you charge subscribers by seat?"
q23 = "total paying subscriber seats?"
q24 = "monthly seat price?"
q25 = "monthly hosting spend for whole company?"

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
answers[q8] = [{"response" : "380"}]
                #380 subscribers
##answers[q9] = [{"response" : "4000"}]
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
answers[q12] = [{"response" : "0.25"},
                #cash bonus equal to 25% of salary for developers
                {"response" : "1.00"},
                #cash bonus equal to 100% of salary for managers (who set their
                #own bonus policy)
                {"response" : "0.15"}]
                #cash bonus equal to 15% of salary for everyone else
                #
                #NOTE: this question should exclude the sales team
answers[q13] = [{"response" : "0.60"},
                #stock bonus equal to 60% of salary for developers
                {"response" : "0.30"},
                #stock bonus equal to 30% of salary for managers
                {"response" : "0.5"}]
                #stock bonus equal to 5% of salary for everyone else
                #
                #NOTE: this question should exclude the sales team
answers[q14] = [{"response" : "0.95"}]
                #keep 95% of revenue, pay out 5% in commissions
answers[q15] = [{"response" : "250000"}]
                #$250,000 LTM marketing spend
answers[q16] = [{"response" : "30000"}]
                #$30,000 in g&a
answers[q17] = [{"response" : "180000"}]
                #$180,000 in annual spend on 3d party developers
##answers[q18] = [{"response" : "6"}]
##                #seats per subscriber
answers[q19] = [{"response" : "50000"}]
                #$50,000 /month for office space for the company
answers[q20] = [{"response" : "We search stuff."}]
answers[q21] = [{"response" : "subscription"}]
answers[q22] = [{"response" : "Yes (charge by seat)"}]
answers[q23] = [{"response" : "1255"}]
                #1255 paying seats (across all subscribers)
answers[q24] = [{"response" : "2000"}]
                #$2k/month per seat
answers[q25] = [{"response" : "3500"}]
                #$3500 per month for hosting
    
