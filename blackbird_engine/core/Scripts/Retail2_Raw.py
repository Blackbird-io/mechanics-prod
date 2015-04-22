#Retail Script 2: Raw

answers = dict()
q1 = "company name?"
q2 = "company industry?"
q3 = "user name?"
q4 = "user position?"
q5 = "number of business units?"
q6 = "unit lifespan in years?"
q7 = "months to unit maturity?"
#
q8 = "annual unit revenue at maturity?"
q9 = "annual revenue at mature stores?"
#
q10 = "average gross margin at a mature unit?"
q11 = "average monthly rent for a unit?"
q12 = "unit employee expense per year?"
q13 = "ltm whole company marketing spend?"
q14 = "ltm whole company overhead, excluding marketing?"

#answer format: track api
#list is the PortalResponse object; dictionary is the ResponseElement object;
#user input in ResponseElement["response"]

answers[q1] = [{"response" : "Wal-Mart"}]
answers[q2] = [{"response" : "Retail"}]
answers[q3] = [{"response" : "Ilya"}]
answers[q4] = [{"response" : "CEO"}]
answers[q5] = [{"response" : "10"}]
answers[q6] = [{"response" : "15"}]
answers[q7] = [{"response" : "36"}]
answers[q8] = [{"response" : "1000000"}]
#one million dollars of revenue at maturity
#
answers[q9] = [{"response" : "1000000"}]
#same question as q8, same answer as q8: one million dollars of revenue at
#maturity
#
answers[q10] = [{"response" : "65"}]
#65% gross margin
#

answers[q11] = [{"response" : "2000"}]
answers[q12] = [{"response" : "300000"}]
#annual unit employee expense of $300,000
#
answers[q13] = [{"response" : "412"}]
#ltm whole company marketing spend of four hundred twelve and 0/100 dollars
#
answers[q14] = [{"response" : "8080"}]
#ltm whole company overhead of eight thousand eighty and 0/100 dollars
#
