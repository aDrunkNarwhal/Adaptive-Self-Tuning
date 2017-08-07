import collections

class ConfigReader:
    """
    Reads a config file and for easy on the fly
    parameter changing.  The default format is
    for reading a YAML file
    """
    def __init__(self,delim=': ',comment='#'):
        """
        Initalize a ConfigReader object
        @params:
            delim       serparater between key and value.
                        Default is ':'
            comment     comment character.  Default is
                        '#'
        @return:
            self        returns the ConfigReader object
        """
        self.delim = delim
        self.comment = comment
        self.data = {}
    
    def read(self,filename):
        """
        Read in a file and separate the contents
        into a dictionary
        @params:
            filename    the name of the config file
        @return:
            None
        """
        f = open(filename,'r')
        lines = f.readlines()
        for l in lines:
            stripped_l = l.lstrip().strip()
            if stripped_l and stripped_l[0] == self.comment:
                continue
            if self.delim in l:
                key,value = stripped_l.split(self.delim)
                self.data[key] = value
        f.close()
        
    def __getitem__(self,key):
        """
        Bultin function to retrive values
        @params:
            key     the key into the data dictionary.
                    If the key is a length 2 list and
                    the key does not exist, then it
                    returns the second value in the list
        @return:
            value   return self.data[key] if key exists.
        """
        if isinstance(key, collections.Iterable) and len(key) == 2:
            if key[0] not in self.data:
                return key[1]
            else:
                value = self.data[key[0]]
        else:
            value = self.data[key]
        
        if value[0] == '[' and value[-1] == ']':
            ans = value[1:-1].split(',')
            if ans[0] == '':
                return []
            return ans
        else:
            return value
    
    def __setitem__(self,key,value):
        """
        Builtin function to modify config values
        after they are loaded
        @params:
            key     key into data dictionary
            value   the value to set into the key
                    location
        @return:
            None
        """
        if type(value) == str:
            self.data[key] = value
        else:
            print "ConfigReader: Value being set needs to be type 'str'"
    
    def __len__(self):
        """
        Builtin funtion that returns the length
        of the number of keys in the data dictionary
        @params:
            None
        @return:
            len     the number of keys in data
        """
        return len(self.data)
