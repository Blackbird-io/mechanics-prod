#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.__init__
"""
This package contains modules that define objects that help guide Blackbird
through model analysis. The objects are designed to measure the impact of each
step in the analysis across several dimensions:

(1) quality of analysis,
(2) attention cost to user,
(3) capacity for additional analysis, and
(4) importance of additional analysis relative to other matters.

Higher level objects can then make determinations based on the state and trend
of these indicators.

====================  ==========================================================
Object                Description
====================  ==========================================================
Functions:
***


Classes:
***
Counter               simple gauge
QualityTracker        specialized gauge to track quality, includes standards
AttentionTracker      specialized gauge to track attention, includes allowance
InterviewTracker      plan and monitor machine-user interview
SelectionTracker      specialized gauge to track MatchMaker selections
Guide                 gauge cluster that guides analysis
====================  ==========================================================
"""




#imports
#[intentionally left blank to prevent circular references]
#n/a




#globals
#n/a
