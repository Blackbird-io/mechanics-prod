#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.InterviewController
"""

Module defines InterviewController class.  
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class InterviewController    selects focal points for a given model; runs on messages
====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals

from . import CompletionTests

from .Controller import Controller
from .PriorityLevel import PriorityLevel
from .Protocol import Protocol




#globals
test_MinComplete = CompletionTests.t_min_quality

#classes
class InterviewController(Controller):
    """

    This class manages protocols that provide a focal point for MatchMaker
    analysis. Daughter of Controller class. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    MR                    instance of Messenger class 
    structure             local state for prioritized approach to interview path
    manageAttention       bool, whether
    defaultProtocolKey    key for default protocol
    makerFunctions        dictionary of maker functions (methods that return
                          protocols applied to a particular model), keyed by
                          complexity score

    FUNCTIONS:
    turnOnAttention()     sets manageAttention to True
    turnOffAttention()    sets manageAttention to False
    buildProtocol()       takes a select() function and binds it to a clean
                          protocol shell
    prioritize()          takes a Model and organizes its interview.path into
                          one or more priorityLevel containers
    process()             takes MQR message, establishes a focal point, returns
                          MQR message with updated model. If method finds that
                          model is complete, runs wrapInterview()
    wrapInterview()       sends out endSession version of incoming message
    makePTCL_AllMin()     returns a protocol that focuses on minimum completion
    makePTCL_AllMax()     INCOMPLETE returns a protocol that focuses on maximum
                          completion
    makePTCL_P1a()        INCOMPLETE returns a protocol that first goes for
                          minimum completion, then tries to forecast attention
                          usage
                          
    ====================  ======================================================
    """
    
    def __init__(self):
        Controller.__init__(self)
        self.structure = None
        self.manageAttention = False
        self.defaultProtocolKey = 1
        self.makerFunctions = {}
        self.makerFunctions[1] = self.makePTCL_AllMin

    def turnOnAttention(self):
        """


        ICtrl.turnOnAttention() -> None


        Method sets instance.manageAttention to True.
        """
        self.manageAttention = True

    def turnOffAttention(self):
        """


        ICtrl.turnOffAttention() -> None


        Method sets instance.manageAttention to False. 
        """
        self.manageAttention = False

    def buildProtocol(self,selectFunction):
        """


        ICtrl.buildProtocol(selectFunction) -> Protocol


        Method creates a new instance of Protocol and binds the selectFunction
        to that instance. Method then returns the protocol instance.
        """
        P = Protocol()
        boundF = selectFunction.__get__(P)
        P.select = boundF
        return P
    
    def prioritize(self, container):
        """


        ICtrl.prioritize(container) -> structure


        ``structure`` is a dictionary of priorityLevel objects keyed by priority.
        The priorityLevel objects contain all important items in container. They
        exclude those items whose priority is currently set to 0.

        ``structure`` thus represents an ordered approach to the container items.
        
        Method generates a brand new structure from scratch on every call and
        expects all items in container to have a fully configured ``guide``
        attribute. 
        """
        structure = {}
        for i in container:
            p = i.guide.priority.current
            if p == 0:
                continue
            else:
                if p not in structure.keys():
                    newPL = PriorityLevel()
                    newPL.append(i)
                    structure[p] = newPL
                else:
                    existingPL = structure[p]
                    existingPL.append(i)
        self.structure = structure
        return structure
        
    def wrapInterview(self,M=None,Q=None,R=None):
        """


        ICtrl.wrapInterview([M=None[,Q=None[,R=None]]]) -> None

        
        If M or Q are not specified, method pulls the active equivalents off
        the instance's MR object.

        Method prepares an endSession message and stores it on the instance's MR
        object using instance.MR.generateMessage(). In the endSession message,
        M and Q are as specified and R is always the global END_INTERVIEW
        sentinel.

        Method sets the interview progress counter in proportion to how far
        along the focal point is in the path.

        This method can also run additional transform or clean up logic. Higher
        level modules may run their own wrapInterview() processes when they
        detect an endSession message, though not all upper-level modules attempt
        such detection.

        """
        if not M:
            M = self.MR.activeModel
        if not Q:
            Q = self.MR.activeQuestion
        R = Globals.END_INTERVIEW
        self.MR.generateMessage(M,Q,R)

    def process(self, msgIn, requestedProtocolKey = None):
        """


        ICtrl.process(msgIn,[requestedProtocolKey = None]) -> msgOut


        The ``process`` method provides the main interface through which other
        Blackbird components can access InterviewController services. For
        example, the Analyzer module call this method on a Model prior to
        running the MatchMaker.

        Method expects:
          --Model to have an ``interview`` attribute that points to a properly
            configued InterviewTracker object.
          --all LineItems in current period financials to have a properly
            configured Guide object with meaningful importance and quality
            standards
            
        Algorithm applied:
          1) check whether Model already has a focal point
          2) if fP exists, check for presence of activeTest
          3) if activeTest in place, run test on fP
          4) if fP doesn't pass activeTest, fP stays constant
          5) if it does, run protocol.next()
          6) return focalPoint

        For this method to work, Model needs to come with a filled out attribute
        at interview.path. 
        """
        #messaging functionality can allow InterviewController to sign off on
        #questions before they go out to user, or bounce them if they are not
        #appropriate under some parameter (ie too much attention)
        Controller.process(self,msgIn)
        Model = self.MR.activeModel
        newFP = None
        oldFP = Model.interview.focal_point
        activeTest = Model.interview.point_standard
        protocolKey = self.defaultProtocolKey
        #can later actually pick up key that caller specifies
        if oldFP and activeTest and not activeTest(oldFP):
            #attributes specified, and oldFP not done yet
            newFP = oldFP
        else:
            #an attribute is missing or oldFP is done, so need to run protocol
            #check if there is already a protocol on the model
            #if so, run it; if not, make new one
            knownProtocol = Model.interview.protocol
            if knownProtocol:
                if knownProtocol.complete:
                    newFP = None
                    #triggers wrapInterview below
                else:
                    newFP = knownProtocol.select(Model)
                    #protocol.select notes newFP, activeTest function on model's
                    #interviewTracker object
            else:
                Model.interview.clear_cache()
                path = Model.interview.path
                newStructure = self.prioritize(path)
                Model.interview.set_structure(newStructure)
                pMaker = self.makerFunctions[protocolKey]
                newProtocol = pMaker()
                Model.interview.setProtocol(newProtocol)
                newFP = newProtocol.select(Model)
        if newFP == None:
            self.wrapInterview(Model)
            #wrapInterview updates self.MR.messageOut
        else:
            if Model.interview.path:
                #
                #update progress status on the interview; use rough rule of
                #thumb that progress is proportional to position in of focal
                #point in path.
                #
                #Note that interview does not have to follow the
                #path currently on the model (other objects can direct the
                #interview by setting new focal points for matchmaker). model
                #may not have a path at all, especially at the beginning, when
                #Starter modules manually establish focal points.
                #
                #Accordingly, wrap logic in exception handler to make sure that
                #Engine does not have to interrupt critical interview flow
                #because of difficulties pinning down the interview progress.
                #Topic module will always increment the progress by 1% for every
                #new question anyways, to make sure the user understands they
                #are moving ahead.  
                #
                try:
                    i = Model.interview.path.index(newFP)
                    #old-fashioned index is most reliable and probably as fast
                    #as any specialized alternative, particularly since focal
                    #point may not be in path
                    #
                    new_progress = i/len(Model.interview.path)
                    new_progress = new_progress * 100
                    new_progress = int(new_progress)
                    Model.interview.setProgress(new_progress)
                    #could wrap this whole thing in an exception handler
                    #
                except ValueError:
                    #some topic could have intentionally redirected the
                    #interview by supplying a focal point from outside the path
                    pass
            self.MR.generateMessage(Model,
                                    self.MR.activeQuestion,
                                    self.MR.activeResponse)
            #prepare self.MR.messageOut manually w updated Model and old Q,R 
        return self.MR.messageOut      
            
    def makePTCL_AllMin(self):
        """


        ICtrl.makePTCL_AllMin() -> Protocol

        
        Returns a protocol object with a custom select() function.
`
        The AllMin protocol steps through each level in an interview.structure,
        in descending order of priority, until every item in a level is min
        complete.

        The AllMin protocol is not attention sensitive.

        Protocol records focal point and active test on Model.interview before
        returning the focal point.
        """
        def min_select(protocol,Model):
            fDone = test_MinComplete
            newFP = None
            #get priority levels in order from hi to lo
            priorities = list(Model.interview.structure.keys())
            priorities.sort()
            priorities = priorities[::-1]
            while not newFP:
                #1) locate highest-priority unfinished level
                #2) test each location until find item that's not 'done'
                #under current definition
                workLevel = None
                for priority in priorities:
                    #step through priorities in descending order
                    level = Model.interview.structure[priority]
                    if not level.finished:
                        workLevel = level
                        workLevel.started = True
                        break
                    else:
                        continue
                else:
                    #if all levels finished, protocol complete, stop work
                    protocol.complete = True
                if protocol.complete:
                    newFP = None
                    break
                else:
                    for i in range(len(workLevel)):
                        line = workLevel[i]
                        doneStatus = fDone(line)
                        if doneStatus:
                            continue
                        else:
                            newFP = workLevel[i]
                            workLevel.ilastTouched = i
                            #could potentially be before prior focal point
                            break
                    else:
                         workLevel.finished = True
                         #went through this level, couldnt find an open item
                         #need to go to next level and repeat search
            Model.interview.set_focal_point(newFP)
            Model.interview.set_point_standard(test_MinComplete)
            return newFP
        minProtocol = self.buildProtocol(min_select)
        minProtocol.name = "allMin"
        return minProtocol
            
    def makePTCL_AllMax(self):
        """


        IC.makePTCL_AllMax() -> Protocol

        
        NOTE: INACTIVE
        
        make a generator function that focuses on each item in financials until
        that item is max complete
        """
        pass
        
    def makePTCL_P1a(self):
        """
        NOTE: OBSOLETE!
        
        Returns generator object
        P1a 

        Generally:
           protocols work one level at a time (L1)
           until that level satisfies some set of functions {F1,[F2...]}
           it then uses a rule of decision (S1) to select the next level
           and repeats
           until all levels are done
        May be able to condense rules into a dictionary format, a la topics
        so protocols can piggy back on each other
        
        !setProtocol should bind the protocol to the model so protocol can view
        the model and all its attributes as self

        P1a (manage for attention):
        starts at highest priority level
        each item in order is focalPoint until it's minCompelte
        after that:
          if no attention left over:
             quit
          else:
             divide left-over attention by number of items
             that's your remaining allowance
             work on each item until hit attention allowance or quality.max
             move on to next one
        if done w level and attention left over, move on to next one        
        """
        pass
##    
##
##        modifiedStructure = []
##        for pL in Model.interview.structure:
##            step1 = [copy.copy(pL),[test_MinComplete],False]
##            step2 = [copy.copy(pL),[test_MaxOrAllowance],False]
##            step3 = [None,None,False]
##            modifiedStructure.extend([step1,step2,step3])
##        def protocol(Model):
##            fP = Model.interview.focalPoint
##            activeTest = Model.interview.activeTest
##            newFP = None
##            if not activeTest(fP):
##                yield fP
##            else:
##                while not newFP:
##                    workingPL = None
##                    workingTests = None
##                    for i in range(len(modifiedStructure)):
##                        #one step at a time
##                        step = modifiedStructure[i]
##                        pL = step[0]
##                        tests = step[1]
##                        done = step[2]
##                        if done:
##                            continue
##                        elif i%2 == 1 and not pL.prepared:
##                            #odd indeces (1,3,5)
##                            #compute attentionAllowance
##                            #should really only run this once per level, at the
##                            #beginning. otherwise, keep reducing allowance per item
##                            #as you go through items (cause total shrinks, and don't
##                            #check how many are open)
##                            remainingAttention = Model.interview.attention.allowance-Model.interview.attention.current
##                            aPerItem = remainingAttention // len(pL)
##                            for item in pL:
##                                item.guide.attention.setAllowance(aPerItem)
##                            workingPL = pL
##                            workingTests = tests
##                            break
##                        else:
##                            workingPL = pL
##                            workingTests = tests
##                            break
##                    else:
##                        #no breaks, every pL is done
##                        Model.interview.complete = True
##                        newFP = "COMPLETE"
##                        #ends the loop
##                    for j in range(len(workingPL)):
##                        item = workingPL[j]
##                        for test in workingTests:
##                            if test(item):
##                                continue
##                            else:
##                                newFP = item
##                                workingPL.iLastTouched = i
##                                #found your focalPoint
##                                break
##                        else:
##                            #move on to next item
##                            continue
##                        #get here if broken out of inner loop
##                        break
##                    else:
##                        workingPL.finished = True
##                        #need to note in mod structure too
##                        #so should go by index.
##            yield newFP
##        protocol.name = "P1a"
##        return protocol

#done1 comes back positive, so need to decide whether to go on
#to next item or keep pushing this one (because all items are
#done w first pass quality anyways)
#
#approach 1: test explicitly. check if any items in priority
#level fail stage 1
#approach 2: test sample. check if next item fails level 1;
#ignores possibility that an external controller might have
#changed something down the line.
#approach 3: bool flags for each type of completion; these are
#going to be misleading unless they are dynamic and essentially
#include full approach 1 logic (that is, a topic may forget to
#toggle the right completeness). in fact, it is probably bad
#design to expect any object outside the InterviewManager to
#even know the standard for completeness.
#
#approach 4: create a more elaborate structure. each ``done``
#standard should correspond to its own copy of priority levels
#e.g.:
#   pl5 = [i1,i5,i7,i8]
#   pl3 = [i2,i3]
#   pl1 = [i4,i6]
#structure = [pl5,pl3,pl1]
#that's current
#modified:
#structure = [(pl5,pl5),(pl3,pl3),(pl1,pl1)]
#that is, a pL copy for every done function
#when a done function is satisfied for a level, say it's 
#finished
#basically, the protocol should make its own modified structure
#i can store modStructure on model.interview
#or in protocol
#in fact, modStructure can be a list of tuples
#[(functions,priorityLevel),(functions,PriorityLevel)]... so on
#here it would be:
#[(done1,pl1),(done2,pl1),(done1,pl2),(done2,pl2)...]
#the protocol would make the modified list
#and may be wouldnt even do a basic check
#like always go through the full process
#or attach current test to the guide element of the item
#or interview. so would have model.interview.focalPoint and
#interivew.currentTest
#if fail currentTEst, stay focal
#if pass, go through full alt Structure, find first unfinished
#tuple, find first item that doesnt satisfy test, return that. 
#use same priority levels as now, w only one bool ``finished``
#
        
#should really put together modified structure list
#where each item is:
#  0) priorityLevel
#  1) list of tests pL must pass
#  2) completion status
#  3) prep function
#  4) prep status
        
