#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: PlatformComponents.Connector
"""

Module defines Connector class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Connector

====================  ==========================================================
"""




#imports:
#n/a




class Connector:
    """
    Class provides a uniform interface for component modules to connect to
    external resources. Easier to use and less error-prone than either absolute
    or relative imports.

    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    activeAnalyticalComponents  pointer to AnalyticalComponents module
    activeExceptions            pointer to BBExceptions module
    activeGuidanceComponents    pointer to GuidanceComponents module
    activeInterviewController   pointer to InterviewController object
    activeModelComponents       pointer to ModelComponents module
    activePlatformComponents    pointer to PlatformComponents module
    activeTagCatalog            pointer to TagCatalog object
    activeTopicCatalog          pointer to TopicCatalog object
    activeValuationComponents   pointer to ValuationComponents module
    activeYenta                 pointer to Yenta object
    marketColor                 pointer to market color module
    ParsingTools                pointer to ParsingTools module

    FUNCTIONS:
    connectAll()                main interface, connects all standard modules
    connectAnalyticalComponents()  connects analytical components module
    connectExceptions()         connects BBExceptions module
    connectGuidanceComponents() connects guidance components module
    connectInterviewController()connects interview controller object
    connectMarketColor()        connects market color module
    connectModelComponents()    connects model components module
    connectParsingTools()       connects ParsingTools module
    connectPlatformComponents() connects platform components module
    connectTagCatalog()         connects tag catalog
    connectTopicCatalog()       connects topic catalog
    connectValuationComponents()connects valuation components module
    connectYenta()              connects yenta object
    ==========================  ================================================
    """
    
    def __init__(self):
        self.activeAnalyticalComponents = None
        self.activeExceptions = None
        self.activeGuidanceComponents = None
        self.activeInterviewController = None
        self.activeModelComponents = None
        self.activePlatformComponents = None
        self.activeTagCatalog = None
        self.activeTopicCatalog = None
        self.activeYenta = None
        self.marketColor = None
        self.ParsingTools = None
        #
        self.DataStructures = None
        self.TagManager = None
        self.QuestionManager
        self.FormulaManager
        self.Tools
        #
        
        
    def connectAll(self,CR):
        """

        CR.connectAll(CR) -> None

        Method connects all standard interface attributes to objects on
        passed-in instance of Connector. Main interface for Connector class;
        equivalent to passing a standard bundle of wires.

        NOTE: connectAll() goes through a fixed, previously defined set of
        methods and will not catch new attributes defined on the reference CR
        object if they are not part of the standard Connector interface. 
        """
        self.connectAnalyticalComponents(CR.activeAnalyticalComponents)
        self.connectGuidanceComponents(CR.activeGuidanceComponents)
        self.connectModelComponents(CR.activeModelComponents)
        self.connectPlatformComponents(CR.activePlatformComponents)
        self.connectParsingTools(CR.ParsingTools)
        self.connectTagCatalog(CR.activeTagCatalog)
        self.connectTopicCatalog(CR.activeTopicCatalog)
        self.connectYenta(CR.activeYenta)
        self.connectInterviewController(CR.activeInterviewController)
        self.connectMarketColor(CR.marketColor)
        self.connectValuationComponents(CR.activeValuationComponents)

    def connectExceptions(self,exModule):
        """

        CR.connectExceptions(exModule) -> None

        Method connects instance to passed-in exceptions module.
        """
        self.activeExceptions = exModule

    def connectAnalyticalComponents(self,acModule):
        """

        CR.connectAnalyticalComponents(acModule) -> None

        Method connects instance to the AnalyticalComponents library.
        """
        self.activeAnalyticalComponents = acModule

    def connectGuidanceComponents(self,guideModule):
        """

        CR.connectGuidanceComponents(guideModule) -> None

        Method connects instance to the GuidanceComponents library.
        """
        self.activeGuidanceComponents = guideModule

    def connectInterviewController(self,iC):
        """

        CR.connectInterviewController(iC) -> None

        Method connects instance to passed-in InterviewController object.
        """
        self.activeInterviewController = iC

    def connectMarketColor(self,mC):
        """

        CR.connectMarketColor(mC) -> None

        Method sets instance.marketColor to argument.
        """
        self.marketColor = mC

    def connectModelComponents(self,modelModule):
        """

        CR.connectModelComponents(modelModule) -> None

        Method connects instance to the ModelComponents library.
        """
        self.activeModelComponents = modelModule

    def connectParsingTools(self,ptModule):
        """

        CR.connectParsingTools(ptModule) -> None

        Method connects instance to the ParsingTools library.
        """
        self.ParsingTools = ptModule

    def connectPlatformComponents(self,platformModule):
        """

        CR.connectPlatformComponents(platformModule) -> None

        Method connects instance to passed-in PlatformComponents module.
        """
        self.activePlatformComponents = platformModule

    def connectTagCatalog(self,tagCatalog):
        """

        CR.connectTagCatalog(tagCatalog) -> None

        Method connects instance to passed-in tag catalog object.
        """
        self.activeTagCatalog = tagCatalog

    def connectTopicCatalog(self,topCatalog):
        """

        CR.connectTopicCatalog(topCatalog) -> None

        Method connects instance to passed-in topic catalog object.
        """
        self.activeTopicCatalog = topCatalog

    def connectValuationComponents(self,vc):
        """

        CR.connectValuationComponents(vc) -> None

        Method connects instance to passed-in ValuationComponents module.
        """
        self.activeValuationComponents = vc

    def connectYenta(self,Y):
        """

        CR.connectYenta(Y) -> None

        Method connects instance to passed-in yenta object.
        """
        self.activeYenta = Y
