Blackbird Engine v.0
README 
May 1, 2015

Engine integrates with the Wrapper through the engine.py module. When running API-spec methods in freestanding or integrated mode, Engine returns objects per API-spec. In particular, Engine serializes e_model objects into a string prior to packaging them into a PortalModel. See Shell.to_portal() and Shell.to_engine() for more on conversion methodology. 

-- Use Shell module to run Engine in command-line mode. 
-- Use Tester module for diagnostics. 
-- Run help() on any module for documentation
-- Tests package includes specific individual tests.
-- Managers package includes the Engine content management systems for Topics, Questions, and Formulas.  
