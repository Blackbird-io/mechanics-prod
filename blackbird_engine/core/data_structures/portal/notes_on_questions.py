"""
Notes on creating questions:

    1. #objectives:
        #1. allow CLP to quickly create an array from spec
            #easy with build_custom_array
            #logic on conditionality will be in Portal itself
        #2. allow QM to build conditional questions
            #should probably just be a set_condition() method
            #so if rule is specified, QM is going to do the thing
            #that way, can build a normal array, then add a condition
            #
            #so if conditional, build 
        #3. allow QM to build mixed questions
            #these require a detailed element spec
            #so QM should go through and build it
        #4. maintain the existing updating and detail fill-out functionality

    2. rules
    element_details and full_spec are either/or devices; cant use both
       full_spec trumps details: if you specify full_spec, QM will ignore your details
    if you want a mixed-type question, you MUST provide a full spec
    specify a rule if you want a conditional toggle (wont work if you put it in full_spec)
    "gating_element" instead of show_if
        will appear first in input_array. response will have the same position
        if you specify a gating element, it will always be active unless a topic later turns it off
    benefits of using a typed question: QM will automatically build out the input array for you


    
    via Portal, could have conditional act as a subtype of mixed, but that makes it hard to then
    have basic question types. though none currently include a condition. 
    
    discourage from using conditional questions    

API changes (ask):
   
   PQ.conditional = bool (False by default)
   if conditional, expect 


To do:

PortalQuestion currently ignores the ``conditional`` attribute
refactor SimplePortal to work 


   #if ``conditional``, CPortal should
            #first get the first resposne
            #if that's false, break the for loop
            #else continue through other active elements
            #so on portal:
                #if full_question.rule:
                    #get element response
                    #if full_question.show_if:
                        #
                    #if response check_truthy:
                        #continue
                        #is_truthy(response, input_element)
                    #else:
                        #break


"""
