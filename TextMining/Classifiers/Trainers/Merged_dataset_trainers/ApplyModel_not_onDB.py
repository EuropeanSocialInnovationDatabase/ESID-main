# -*- coding: utf-8 -*-
from Basic_experiments import UniversalClassifier

if  __name__ == '__main__':
    wayback_bar = """ <![endif]   BEGIN WAYBACK TOOLBAR INSERT   success  fail   NEXT/PREV MONTH NAV AND MONTH INDICATOR   Oct  MAY  Jun   NEXT/PREV CAPTURE NAV AND DAY OF MONTH INDICATOR   14   NEXT/PREV YEAR NAV AND YEAR INDICATOR"""
    wayback_bar2 = """About this capture  COLLECTED BY  		Organization:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  Collection:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  TIMESTAMPS   END WAYBACK TOOLBAR INSERT   [if lt IE 7]><p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p><![endif]"""

    content = """The name of someone receiving a payment will be as important as their banking details for the first time from next summer, in an attempt to combat fraud.

At present, anyone wanting to transfer money enters the intended recipient's name, account number and sort code. However, the name is not checked.

Under plans from the UK's payments operator, the sender will be alerted if the name does not match the account.

Banks have been accused of dragging their heels in introducing the system.

It is designed to combat cases when fraudsters mimic a genuine business and attempt to trick people into sending money to an account controlled by the con-artist.

Details of how the "confirmation of payee" system will work have been revealed by Pay.UK - the operator which oversees the UK's major payments systems.
How Confirmation of Payee will work

When setting up a new payment, or amending an existing one, banks will be able to check the name on the account of the person or organisation you are paying.

    If you use the correct account name, you will receive confirmation that the details match, and can proceed with the payment
    If you use a similar name to the account holder, you will be provided with the actual name of the account holder to check. You can update the details and try again, or contact the intended recipient to check the details
    If you enter the wrong name for the account holder you will be told the details do not match and advised to contact the person or organisation you are trying to pay
"""
    objective_cls = UniversalClassifier()
    objective_cls.load_RF_words_only("Objectives_RF")
    actors_cls = UniversalClassifier()
    actors_cls.load_RF_words_only("Actors_RF")
    outputs_cls = UniversalClassifier()
    outputs_cls.load_RF_words_only("Outputs_RF")
    innovativeness_cls = UniversalClassifier()
    innovativeness_cls.load_RF_words_only("Innovativeness_RF")
    si_cls = UniversalClassifier()
    si_cls.load_RF_words_only("SI_RF")
    message = ""
    option = "v7 classifier origninal unbalanced dataset, 9/10/2018"
    objective = 0
    actors = 0
    outputs = 0
    innovativeness = 0
    document_text = content
    if "404" in document_text or "page not found" in document_text.lower():
        message = "Page not found"
    elif "domain for sale" in document_text.lower() or "buy this domain" in document_text.lower() or "find your perfect domain" in document_text.lower() or "domain expired" in document_text.lower():
        message = "Domain for sale"
    elif len(document_text)<350:
        message = "Text smaller than 350 characters"
    else:
        objective = objective_cls.predict_words_only([document_text])[0]
        actors = actors_cls.predict_words_only([document_text])[0]
        outputs = outputs_cls.predict_words_only([document_text])[0]
        innovativeness = innovativeness_cls.predict_words_only([document_text])[0]
        si = si_cls.predict_words_only([document_text])[0]
    print(message)
    print("Objective:"+str(objective))
    print("Actors:" + str(actors))
    print("Outputs:" + str(outputs))
    print("Innovativeness:" + str(innovativeness))
    print("Social Innovation:" + str(si))
    print("Done!")