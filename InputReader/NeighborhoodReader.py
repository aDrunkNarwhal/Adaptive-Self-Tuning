def read(filename):
    """
    Reads in a neighborhood file and returns
    a dictionary of stations as the keys
    and the neighbor list as the values
    @params:
        filename    the file path of the
                    neighborhood file
    @return:
        data        a dictionary where the
                    keys are station names
                    and values are a list of
                    station names
    """
    sep = '-'
    data = {}
    f = open(filename,'r')
    lines = f.readlines()
    for l in lines:
        split_l = l.strip().split(',')
        data[split_l[0]+sep+split_l[1]] = combineStationChannel(split_l[2:],sep)
    return data

def combineStationChannel(l,sep='-'):
    i = 0
    result = []
    while i < len(l) and i+1 < len(l):
        if l[i] != '' and l[i+1] != '':
            result.append(l[i] + sep + l[i+1])
        i += 2
    return result