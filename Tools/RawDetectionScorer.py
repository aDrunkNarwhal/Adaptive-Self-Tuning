def score(ARRIVALs,GTs,step,score_delay=3600,sr=200):
    arrs = splitByStation(ARRIVALs,delay=score_delay*sr) #TODO: USE SCORE DELAY
    gts = splitByStation(GTs,delay=score_delay*sr) #TODO: USE SCORE DELAY
    false,missed,matched = 0,0,0
    gt = sum([len(gts[s]) for s in gts])
    arrivals = sum([len(arrs[s]) for s in arrs])
    
    for s in arrs:
        t_false,t_missed,t_matched = scoreStation(arrs[s],gts[s],step*sr)
        false += t_false
        missed += t_missed
        matched += t_matched
        
    s =  str(missed) + "," + str(false) + "|"
    s += str(float(missed) / float(gt)*100) + "," + str(float(false) / float(arrivals)*100)
    
    return s

def splitByStation(arrs,delay=0):
    new = {}
    
    for a in arrs:
        if a['time'] < delay:
            continue
        if a['station'] not in new:
            new[a['station']] = [a]
        else:
            new[a['station']].append(a)
    
    return new

def scoreStation(sta_arrs,sta_gts,window):
    arrs = sorted(sta_arrs,key=lambda x: x['time'])
    gts = sorted(sta_gts,key=lambda x: x['time'])
    
    false,missed,matches = 0,0,0
    
    arr_index = 0
    gts_index = 0
    
    while arr_index < len(arrs) and gts_index < len(gts):
        arr_time = arrs[arr_index]['time']
        gt_time = gts[gts_index]['time']
                
        if gt_time < (arr_time - window):
            missed += 1
            gts_index += 1
        elif gt_time > (arr_time + window):
            false += 1
            arr_index += 1
        else: # Its a Match! +/- wz
            matches += 1;
            arr_index += 1;
            gts_index += 1;
    
    false += len(arrs) - arr_index
    missed += len(gts) - gts_index
    
    return false,missed,matches
