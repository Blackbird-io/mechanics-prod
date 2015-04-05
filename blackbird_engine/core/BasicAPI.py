#new simple test
#for running through the api methods only
#start w starting message from Portal
#call Shell.process_interview(), then call Portal.process(), which should work w script
#until get message that says stop_interview
#

#imports
import BBGlobalVariables as Globals
import Shell as Engine
import SimplePortal as Portal

from Scripts import Retail2_Raw




#globals
retail_script = Retail2_Raw.answers
Portal.set_script(retail_script)
#
msg_0 = Portal.starting_message
final_message = None
#
loop = True
while loop:
    msg_1 = Engine.process_interview(msg_0)
    msg_mqr = Engine.to_engine(msg_1)
    #
    status = Globals.checkMessageStatus(msg_mqr)
    if status == Globals.status_endSession:
        final_message = msg_1
        break
    else:
        msg_2 = Portal.process(msg_1)
        msg_0 = msg_2
        continue
#
#compare results based on summaries
#
#
#then also make a test to check for landscape_summary
#and for sluts
#
