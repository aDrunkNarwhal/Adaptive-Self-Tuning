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
    window = sr * 5 #step 
    gt = 0
    dets = 0
    matches = 0
    false_dets = 0
    missed_dets = 0
    found_dets = 0
    start_score = score_delay * sr
    
    gts_sorted = sorted(gts, key=lambda a: a['time'])
    arr_sorted = sorted(arrivals, key=lambda a: a['time'])
    
    hours = int(max(gts_sorted[-1]['time'],arr_sorted[-1]['time']) / (sr*3600)) + 1
    
    gt_events = genEventTimes(gts_sorted,start_score,window)
    arr_events = genEventTimes(arr_sorted,start_score,window)
    
    gt = sum([x['nDef'] for x in gt_events])
    dets = sum([x['nDef'] for x in arr_events])
    
    gt_index = 0
    arr_index = 0
    
    GT = [{} for ii in xrange(hours)]
    
    MISSED = [{} for ii in xrange(hours)]
    FALSE = [{} for ii in xrange(hours)]
    MATCHES = [{} for ii in xrange(hours)]
        
    while gt_index < len(gt_events) and arr_index < len(arr_events):
        gt_time = gt_events[gt_index]['start_time']
        arr_time = arr_events[arr_index]['start_time']
        gt_hour = int(gt_time / (sr * 3600))
        arr_hour = int(arr_time / (sr * 3600))
        
        for s in gt_events[gt_index]['stations']:
            if s not in GT[gt_hour]:
                GT[gt_hour][s] = 1
            else:
                GT[gt_hour][s] += 1
        
        if gt_time < (arr_time - window):
            missed_dets += gt_events[gt_index]['nDef']
            for s in gt_events[gt_index]['stations']:
                if s not in MISSED[gt_hour]:
                    MISSED[gt_hour][s] = 1
                    FALSE[gt_hour][s] = 0
                    MATCHES[gt_hour][s] = 0
                else:
                    MISSED[gt_hour][s] += 1
            gt_index += 1
        elif gt_time > (arr_time + window):
            false_dets += arr_events[arr_index]['nDef']
            for s in arr_events[arr_index]['stations']:
                if s not in FALSE[arr_hour]:
                    FALSE[arr_hour][s] = 1
                    MISSED[arr_hour][s] = 0
                    MATCHES[arr_hour][s] =0
                else:
                    FALSE[arr_hour][s] += 1
            arr_index += 1
        else: # Its a Match! +/- wz
            for s in gt_events[gt_index]['stations']:
                if s in arr_events[arr_index]['stations']:
                    if s not in MATCHES[arr_hour]:
                        MATCHES[arr_hour][s] = 1
                        MISSED[arr_hour][s] = 0
                        FALSE[arr_hour][s] = 0
                    else:
                        MATCHES[arr_hour][s] += 1
                    matches += 1
                else:
                    if s not in MISSED[arr_hour]:
                        MISSED[arr_hour][s] = 1
                        FALSE[arr_hour][s] = 0
                        MATCHES[arr_hour][s] =0
                    else:
                        MISSED[arr_hour][s] += 1
                    missed_dets += 1
            for s in arr_events[arr_index]['stations']:
                if s not in gt_events[gt_index]['stations']:
                    found_dets += 1
            arr_index += 1
            gt_index += 1
    
    false_dets += sum([x['nDef'] for x in arr_events[arr_index:]])
    missed_dets += sum([x['nDef'] for x in gt_events[gt_index:]])
    
    
    s = "HOUR,STA,MATCHED,MISSED,FALSE\n"
    for h in xrange(hours):
        for sta in sorted(FALSE[h].keys()):
            s += str(h) + "," + sta + "," + str(MATCHES[h][sta]) + "," + str(MISSED[h][sta]) + "," + str(FALSE[h][sta]) + "\n"
    """
    
    s = "HOUR,STA,NUM\n"
    for h in xrange(hours):
        for sta in sorted(GT[h].keys()):
            s += str(h) + "," + sta + "," + str(GT[h][sta]) + "\n"
    """
    print s
    import sys
    sys.exit()
    
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
