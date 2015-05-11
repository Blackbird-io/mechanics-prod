#alt lifecycle
#

#figure out what methods BU.extrapolate uses.

class LifeCycle:
    """
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA:
    age                   float, distance from date_of_birth to ref_date, in seconds;
                          can be negative but only up to magnitude of gestation_period
                          (ie, no age prior to conception)
    alive
    dead
    date_of_birth         float, date_of_conception + gestation
    date_of_conception    float, POSIX timestamp
    date_of_death
    duration              float, expected life, in seconds
    gestation_period      float, time from conception to birth, in seconds             
    ref_date
    
    
    percent               float, age / life_span * 100
    stages                dict, contains endpoints and names

    FUNCTIONS:
    kill()                kill instance
    set_duration()
    add_stage()
    setLifeStages()       sets lifestages for instance
    setRefDate()          sets refDate for instance
    showLifeStages()      returns pretty string of life stages
    ====================  ======================================================
    """
    #life begins at conception
    def __init__(self):
        #
        #could combine alive/dead/killed into a status; options: None, alive, dead
        #None prior to conception
        #alive after
        #dead after
        #
        #self.status = None
        #use a property here, cant delete
        #
        #
        self.stages = dict()
        self.stages["end_points"] = list()
        self.stages["names"] = dict()
        #names is i: name
        #implement names as dictionary to make sure names always has same length
        #as end_points
        #
        #should be something thats easy to traverse linearly
        #so if you know life.percent, you can quickly figure out what stage obj
        #is in.
        #
        #to do that ... can have range objects, then easy to check for int?
        #numbers in order:
            #stage points = [0,10,25,30,45,100]
            ##always start w 0 and end in 100
            #if age > 0:
                #for i in range(len(stage_points)-1):
                    #stage_number = i
                    #start = stage_points[i]
                    #end = stage_points[(i+1)]
                    #stage = range(start, end)
                    #if int(self.percent) in stage:
                        #self.stage_name = self.stages["names"][stage_number]
                        #break
                    #else:
                        #continue
                #
            #can have check_stages() too? 
        #
        self.period_name = blah
        #managed attr
        self.age = blah
        #managed attr, ref - (conception + gestation)
        self.date_of_birth = blah
        #managed attr, := self.date_of_conception + self.gestation_period
        #

    def kill(self, timestamp = None):
        if not timestamp:
            timestamp = time.time()
        self.death_timestamp = timestamp

    def set_ref_date(self, timestamp):
        self.ref_date = timestamp

    def set_dob(self, timestamp):
        #should automatically set date of conception
        #then go from there
        
    def set_gestation(self, length_in_seconds):
        pass

    def set_conception_date(self, timestamp):
        pass

    def set_duration(self, length_in_seconds):
        self.duration = length_in_seconds

    def add_stage(self, stage):
        #check that stage has start, end, and name
        #
        #should be able to take objects and dictionaries as stage
        #stage should be a dictionary w known keys
        #stage_starts = int(stage["starts"])
        #self.stages["all"][stage_starts] = stage
        #self.organize_stages()
        

    def organize_stages(self, candidates = None):
        ##gestation is not a stage
        ##
        #
        #candidates = sort(self.stages["all"].keys())
        ##filter out any keys below 0 or above 100
        ##take set(range(0,100)). candidates = candidates & demand#
        ##
        ##
        #then, take min of the candidates
        ##then, take min of the candidates; append it to endpoints list
        ##take next min, append it
        ##and so on
        ##alternatively, filter out all candidates that are smaller than
        ##end point of this guy. then repeat min and so on. 
        #
    
        
