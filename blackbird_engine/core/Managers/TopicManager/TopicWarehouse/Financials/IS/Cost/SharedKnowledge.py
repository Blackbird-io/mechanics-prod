industry_gross_margin= {}
#keys to dictionary are known industries
#items are a tuple of strong,medium,weak margins
industry_gross_margin["retail"] = (0.75,0.65,0.55)
industry_gross_margin["distribution"] = (0.30,0.20,0.10)
industry_gross_margin["business services"] = (0.80,0.60,0.50) 
industry_gross_margin["saas"] = (0.95,0.85,0.75)
industry_gross_margin["epc"] = (0.50,0.35,0.20)
#industry_gross_margin["healthcare-primary"] 
#industry_gross_margin["SpecialtyFinance"] 
industry_gross_margin[None] = (0.60,0.50,0.40)


software = dict()
software["development expense allocation to product cost"] = 0.20
