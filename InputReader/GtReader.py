def read(filename,start_time,sample_rate,start,end,minSNR=0.0):
    """
    Reads in a file and returns a list of arrivals
    @params:
        filename        file path of where the gt
                        arrival file is
        start_time      the clock time of the start
                        of the stations
        sample_rate     the sample rate of the
                        stations
        start           The start time of when to
                        consider arrivals as
                        ground truth
        end             the end time of when to
                        consider arrivals as ground
                        truth
        minSNR          the minimum snr for an arrival
                        to be considered ground truth.
                        Default is 0.0 (aka. all
                        arrivals)
    @return:
        data            a list of ground truth 
                        arrivals
    """
    data = []
    f = open(filename,'r')
    for l in f.readlines():
        split_l = l.strip().split(',')
        if float(split_l[3]) >= minSNR:
            temp = {}
            temp['station'] = split_l[1] + '-' + split_l[0] # STA-CHAN
            temp['time'] = int((float(split_l[2]) - start_time) * sample_rate)
            temp['snr'] = float(split_l[3])
            if temp['time'] >= start and temp['time'] <= end:
                data.append(temp)
            del(temp)
    return data
