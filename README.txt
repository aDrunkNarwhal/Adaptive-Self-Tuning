************************************************************************************************************************
Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC . Under the terms of Contract DE-NA0003525 with National Technology and Engineering Solutions of Sandia, LLC , the U.S. Government retains certain rights in this software.
************************************************************************************************************************

Concatenate.py
    $ python Concatenate.py "PATH/TO/FILES/*" "OUTPUTNAME" OVERLAP_SECS
    
    The first argument is a regex for all the files that you want to concatenate
    together.
    
    The second argument is what you want the output to be named
    (aka. the concatenated file).
    
    The third argument is how many seconds of overlap there is between the files.

Update_Header.py
    $ python Update_Header.py "LIST_OF_CHANNEL_NAMES.txt" "SEISMIC_DATA.DAT" "OUTPUTNAME"
    
    The first arugment is a file with the list of channel names in order.  There
    is an example file "FWU_STA_CHANs.txt".  The first row is the Station name
    and all other rows are the Channel names in order.
    
    The second argument is the seismic data file.
    
    The third argument is the name for the output file.  Keep in mind that the 
    output format is MSEED.
