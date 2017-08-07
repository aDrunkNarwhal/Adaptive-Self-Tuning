import numpy as np

class MajorityRules:
    """
    A DecisionMaker that changes actions based on
    a majorirty vote. Majority is assumed to be
    correct, so if a given sensor is in the
    minority then that sensor is adjusted accordingly.
    If it saw something and the majorirty did not,
    that sensor is is made less sensitive. And if the
    sensor did not see something and the majority did,
    then that sensor is made more sensitive.
    """
    def __init__(self,sta,init_action,nl,ss=0.1,dr=-0.002):
        """
        Initialize a MajorityRules DecisionMaker
        @params:
            sta             the name of the station
            init_action     the value to initialize the
                            action to
            nl              the neighborhood list for the 
                            station specified
            ss              maximum step size for changing
                            an action. Default is '0.1'
        @return:
            self            returns the MajorityRules object
        """
        self.station = sta
        self.prev_action = init_action
        self.neighbors = nl
        self.max = 4.0
        self.min = 1.0
        self.step = ss
        self.decay_rate = dr
    
    def getAction(self,trigs,avg_snr):
        """
        Get the next action
        @params:
            trigs           a dictionary where the keys are the
                            station names and the values are a
                            '1' if the station detected and a
                            '0' if the station did not detect
            avg_snr         a dictionary where the keys are the
                            station names and the values are
                            the average snr for a given station
                            over the current time_step
        @return:
            curr_action     the next action to be set
        """
        if self.step > 0.0:
            curr_action = self.prev_action
            majority,minority = self.splitStations(trigs)
            if majority and minority and self.station in minority:
                curr_action += self.punish(avg_snr,detect=(trigs[self.station]==1))
            else:
                curr_action += self.decay(avg_snr)
            
            if curr_action < self.min:
                curr_action = self.min
            elif curr_action > self.max:
                curr_action = self.max
    
            self.prev_action = curr_action
        return self.prev_action
        
    def splitStations(self,trigs):
        """
        Splits the neighborhood list plus station into
        two groups; those who detected and those who did
        not. The first one return is majority group.
        @params:
            trigs               a dictionary where the keys are the
                                station names and the values are a
                                '1' if the station detected and a
                                '0' if the station did not detect
        @return:
            majority,minority   two lists of stations; the majority
                                group and the minority group 
        """
        detect,no_detect = [],[]
        for sta in [self.station] + self.neighbors:
            if trigs[sta] >= 1:
                detect.append(sta)
            else:
                no_detect.append(sta)
        
        if len(detect) > len(no_detect):
            return detect,no_detect
        elif len(detect) < len(no_detect):
            return no_detect,detect
        else:
            return None,None
    
    def punish(self,snr,detect=True):
        """
        Adjust the action up or down
        @params:
            snr     the average snr over last time step
            detect  whether or not the station detected
                    last time step. Default 'True'
                    (Currently not be used)
        @return:
            value   updated action value
        """       
        if detect:
            value = self.tanh_jump(self.step,snr,1.0,mod=-1)
        else:
            value = self.decay(snr)
        
        return value
        
    def decay(self,snr):
        """
        Small decay of the action value to make the
        station more sensitive
        @params:
            snr     the average snr over last time step
        @return:
            value   updated action value
        """
        return self.tanh_jump(self.decay_rate,snr,1.0,mod=1)
        #return self.decay_rate  
        #return -0.035 * self.step  #-0.002
        
    def tanh_jump(self,max_step,snr,percent=1.0,mod=-1):
        """
        Uses a tanh function to determine how much to adjust
        the action value
        @params:
            snr         the average snr over last time step
            percent     the percent of the jump to use. Default
                        '1.0' (aka. 100%)
            mod         for making the change negative or positive
        @return:
            jump        the amount to change the action value
        """
        alpha = (self.max + self.min) / 2.0
        return 0.5*(1 + mod * np.tanh(self.prev_action - alpha)) * percent * max_step
        #return 0.5*(1 + mod * np.tanh(snr - self.prev_action - alpha)) * percent * self.step
        #return np.tanh(snr - self.prev_action) * percent * self.step  
        
    def __str__(self):
        """
        Builtin funtion to transform a MajorityRules object
        into a str object
        @params:
            None
        @return:
            string  str object for MarjorityRules info
        """
        string  = "station:    " + self.station + '\n'
        string += "action:     " + str(self.prev_action) + '\n'
        string += "neighbors:  " + str(self.neighbors) + '\n'
        string += "max_action: " + str(self.max) + '\n'
        string += "min_action: " + str(self.min)
        
        return string
        
    def __repr__(self):
        """
        Builtin function that transforms a MajorityRules object
        into a str object
        @params:
            None
        @return:
            string  str object for MarjorityRules info
        """
        string  = "station:    " + self.station + ','
        string += "action:     " + str(self.prev_action) + ','
        string += "neighbors:  " + str(self.neighbors) + ','
        string += "max_action: " + str(self.max) + ','
        string += "min_action: " + str(self.min)
        
        return string
