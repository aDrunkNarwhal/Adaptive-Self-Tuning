num_stations = 48
first_half = 24
sta = "FWU"
RESULT = ""
for i in range(1,first_half + 1):
    line = sta + ',' + str(i)
    for chan in range(1,num_stations + 1):
        if i != chan:
            line += ',' + sta + ',' + str(chan)
    RESULT += line + '\n'
for j in reversed(range(first_half+1,num_stations+1)):
    line = sta + ',' + str(j)
    for chan in range(1,num_stations + 1):
        if j != chan:
            line += ',' + sta + ',' + str(chan)
    RESULT += line + '\n'
f = open("Neighborhoods/FWU_FULL_CONNECT.csv",'w')
f.write(RESULT)