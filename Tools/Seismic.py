import obspy
from obspy.signal.trigger import classic_sta_lta,trigger_onset
import numpy as np
import math

def getStaLtaValues(stations,start,duration,sta_win,lta_win,sr,sep='-',quiet=True):
    """
    Creates lists of STA/LTA values for each station
    @params:
        stations    a list of stations created by
                    obspy.read
        start       the start time in seconds
        duration    the duration of times to consider
                    in seconds
        sta_win     the STA window size in seconds
        lta_win     the LTA window size in seconds
        sr          the sampling rate in Hz
        quiet       if 'True', no output to screen.
                    Default is 'True'
    @return:
        values      a dictionary of STA/LTA values
                    where the keys are the station
                    names
    """
    if not quiet:
        print "STA/LTA CALCULATIONS..."
    values = {}
    
    for sta in stations:
        values[sta.stats.station+sep+sta.stats.channel] = classic_sta_lta(
                               sta.data[int(start*sr):int((start+duration)*sr)],
                               int(sta_win*sr),int(lta_win*sr)) 
    if not quiet:
        print "done"
    return values

def getStations(data_dir,data_files,bandpass_low,bandpass_high,quiet=True):
    """
    Creates station objects generated form obspy.read
    @params:
        data_dir        the directory where the waveform
                        files are located
        data_files      the specific files to grab from
                        data_dir. If empty is reads all
                        files located in data_dir
        bandpass_low    filter out frequencies less
                        than this value
        bandpass_high   filter out frequencies greater
                        than this value
        quiet           if 'True', no output to screen.
                        Default is 'True'
    @return:
        stations        a list of station objects created
                        by obspy.read
    """
    if not quiet:
        print "READING STATIONS..."
    stations = None
    if data_files:
        for f in data_files:
            if stations == None:
                stations = obspy.read(data_dir + '/' + f)
            else:
                stations += obspy.read(data_dir + '/' + f)
    else:
        stations = obspy.read(data_dir + '/*')
    if not quiet:
        print "\tapplying filter..."
    if bandpass_low != None and bandpass_high != None:
        applyFilter(stations,bandpass_low,bandpass_high) 
    if not quiet:    
        print "done"   
    
    return stations
    
def applyFilter(stations,bandpass_low,bandpass_high):
    """
    Does a bandpass filter for all stations
    @params:
        stations        a list of station objects created
                        by obspy.read
        bandpass_low    filter out frequencies less
                        than this value
        bandpass_high   filter out frequencies greater
                        than this value
    @return:
        None
    """
    for sta in stations:
        sta.filter('bandpass',freqmin=bandpass_low,freqmax=bandpass_high)

def getTriggerOnset(levels,start,end,TD,TL,RL,RD):
    onset = None
    offset = None
    for index,l in enumerate(levels[start:end]):
        if l >= TL:
            if onset == None and offset == None:
                onset = index
            elif offset != None and index - offset <= RD:
                offset == None
        elif l <= RL:
            if onset != None and offset == None:
                offset = index
            
            if onset != None and offset != None and index > offset + RD:
                if offset - onset >= TD:
                    break
                else:
                    onset = None
                    offset = None
                
    if onset != None and offset == None:
        offset = end
    if offset != None and offset - onset > TD:
        return onset,offset
    else:
        return None,None

def getTriggers(levels,sta,curr_time,sr,time_step,trigger_duration,reset_duration,DMs):
    """
    Returns a list of trigger times for a given station
    @params:
        levels              STA/LTA values for a station
        sta                 station name
        curr_time           start time to process on
        sr                  sampling rate in Hz
        time_step           window size to process on
        trigger_duration    the length of time in seconds
                            the STA/LTA needs to stay
                            above the trigger level
                            in order to be considered
                            a trigger
        DMs                 a list of DecisionMakers
    @return:
        list                a list of triggers times
                            for a given station
    """
    end_time = curr_time+int(sr*(time_step+trigger_duration))
    if end_time > len(levels[sta]):
        end_time = len(levels[sta])
    
    #onset,offset = getTriggerOnset(levels[sta],curr_time,end_time,
    #                trigger_duration*sr,
    #                DMs[sta].prev_action,DMs[sta].prev_action,reset_duration*sr)
    
    #if onset != None:
    #    return [onset]
    #else:
    #    return []
        
    return [x[0] for x in trigger_onset(
            levels[sta][curr_time:end_time],
            DMs[sta].prev_action,
            DMs[sta].prev_action)
            if (x[1]-x[0]) >= trigger_duration * sr]

def getAvgSNR(sta,levels,curr_time,sr,time_step):
    """
    Calculate the average snr for a given station
    @params:
        sta         station name
        levels      STA/LTA values for a station
        curr_time   start time to process on
        sr          sampling rate in Hz
        time_step   window size to process on
    @return:
        avg         the average snr for a sensor
                    over a specified time range
    """
    end_time = curr_time+int(sr*time_step)
    if end_time > len(levels[sta]):
        end_time = len(levels[sta])
    return np.mean(levels[sta][curr_time:end_time])

def getDetections(levels, curr_time,sr,time_step,trigger_duration,reset_duration,DMs):
    trigs = {}
    avg_snr = {}
    temp_arrivals = []
    
    for sta in DMs.keys():
        result = getTriggers(levels,sta,
                            curr_time,sr,
                            time_step,
                            trigger_duration,
                            reset_duration,DMs)

        avg_snr[sta] = getAvgSNR(sta,levels,curr_time,sr,time_step) #FIX THIS
                    
        if result:
            temp_arrivals.append({'station':sta,'snr':levels[sta][curr_time+result[0]],'time':curr_time + result[0]})
            trigs[sta] = 1
        else:
            trigs[sta] = 0
        del result
    
    return trigs,avg_snr,temp_arrivals

def findFirstDetect(arrivals):
    time = None
    for arr in arrivals:
        if time == None or arr['time'] < time:
            time = arr['time']
    return time