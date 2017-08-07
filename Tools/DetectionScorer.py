def score(arrivals,gts,step,score_delay=3600,sr=200):
    """
    Takes in the arrivals from the algorithm and the ground
    truth table and outputs stats of missed and false detections
    @params:
        arrivals        a list of arrivals from the dynamic
                        algorithm
        gts             a list of ground truth arrivals
        step            agreement window size for an event
        minStaAgree     The number of stations that need to
                        all see an event within the step window.
                        Default is '2'
        score_delay     The number of seconds to pass before
                        we start scoring. Default is '3600' (1hr)
        sr              the sampling rate of the wave form.
                        used to convert seconds to data points
    @return:
        s               a str object containing the score of
                        the algorithm
    """
    window = sr * step 
    gt = 0
    dets = 0
    matches = 0
    false_dets = 0
    missed_dets = 0
    found_dets = 0
    start_score = score_delay * sr
    
    gts_sorted = sorted(gts, key=lambda a: a['time'])
    arr_sorted = sorted(arrivals, key=lambda a: a['time'])
        
    gt_events = genEventTimes(gts_sorted,start_score,window)
    arr_events = genEventTimes(arr_sorted,start_score,window)
    
    gt = sum([x['nDef'] for x in gt_events])
    dets = sum([x['nDef'] for x in arr_events])
        
    gt_index = 0
    arr_index = 0
    
    MISSED = {}
    FALSE = {}
    MATCHES = {}
    
    while gt_index < len(gt_events) and arr_index < len(arr_events):
        gt_time = gt_events[gt_index]['start_time']
        arr_time = arr_events[arr_index]['start_time']
        
        if gt_time < (arr_time - window):
            missed_dets += gt_events[gt_index]['nDef']
            for s in gt_events[gt_index]['stations']:
                if s not in MISSED:
                    MISSED[s] = 1
                    FALSE[s] = 0
                    MATCHES[s] =0
                else:
                    MISSED[s] += 1
            gt_index += 1
        elif gt_time > (arr_time + window):
            false_dets += arr_events[arr_index]['nDef']
            for s in arr_events[arr_index]['stations']:
                if s not in FALSE:
                    FALSE[s] = 1
                    MISSED[s] = 0
                    MATCHES[s] =0
                else:
                    FALSE[s] += 1
            arr_index += 1
        else: # Its a Match! +/- wz
            for s in gt_events[gt_index]['stations']:
                if s in arr_events[arr_index]['stations']:
                    if s not in MATCHES:
                        MATCHES[s] = 1
                        MISSED[s] = 0
                        FALSE[s] = 0
                    else:
                        MATCHES[s] += 1
                    matches += 1
                else:
                    if s not in MISSED:
                        MISSED[s] = 1
                        FALSE[s] = 0
                        MATCHES[s] =0
                    else:
                        MISSED[s] += 1
                    missed_dets += 1
            for s in arr_events[arr_index]['stations']:
                if s not in gt_events[gt_index]['stations']:
                    found_dets += 1
            arr_index += 1
            gt_index += 1
    
    false_dets += sum([x['nDef'] for x in arr_events[arr_index:]])
    missed_dets += sum([x['nDef'] for x in gt_events[gt_index:]])
        
#    s =  "EVENT SCORER" + '\n'
#    s += "gt events:        "+str(gt) + '\n'
#    s += "events detected:  "+str(dets) + '\n'
#    s += "matches:          "+str(matches) + '\n'
#    s += "found:            "+str(found_dets) + '\n'
#    s += "false:            "+str(false_dets) + "  " + str(float(false_dets) / float(dets)*100) + '\n'
#    s += "missed:           "+str(missed_dets) + "  " + str(float(missed_dets) / float(gt)*100)
    
    s = str(missed_dets) + "," + str(false_dets) + "|" + str(float(missed_dets) / float(gt)*100) + "," + str(float(false_dets) / float(dets)*100)
    
#    s = "PER STATION SCORER:\nSTA,MATCHED,MISSED,FALSE\n"
#    for sta in sorted(FALSE.keys()):
#        s += sta + "," + str(MATCHES[sta]) + "," + str(MISSED[sta]) + "," + str(FALSE[sta]) + "\n"
#    
#    print s
    
    return s
    
def genEventTimes(arrivals,start,wz):
    """
    Determines event times for the list of arrivals given
    @params:
        arrivals        a list of arrivals  
        start           the time step to start generating
                        event times
        wz              the window size for station agreement
        minStaAgree     the minimum number of stations agreement
                        for an event to be considered. Default
                        is '1', which correlates that all
                        arrivals are considered an event
    @return:
        results          a list of event times
    """
    
    results = []
    i = 0
    while i < len(arrivals) and arrivals[i]['time'] < start:
        i += 1
    while i < len(arrivals):
        temp_result = {'stations':[],'start_time':None,'end_time':None,'nDef':0}
        addStationResult(temp_result,arrivals[i],wz)
        i += 1
        while i < len(arrivals) and arrivals[i]['time'] <= temp_result['end_time']:
            addStationResult(temp_result,arrivals[i],wz)
            i += 1
        results.append(temp_result)
        del temp_result
    return results

def addStationResult(result,sta,wz):
    """
    Add a station to an event result
    @params:
        result  current result
        sta     station to be added
        wz      window size of agreement
    @return:
        None
    """
    result['stations'].append(sta['station'])
    result['nDef'] += 1
    if result['start_time'] == None:
        result['start_time'] = sta['time']
        result['end_time'] = sta['time'] + wz
