#### import ####

import os
import json

#### get WMDR notation #####

def get_WMDR_notation(csv_source,label):

    # open dictionary
    with open(os.getcwd()+'/dictionaries/'+label+'_dictionary.json') as f:
        dictionary = json.loads(f.read())

   # get WMDR Codes Registry number from dictionary
    variables = csv_source[label]
    variables = [x.strip() for x in variables.split(',')]
    wmdr_codes = [dictionary.get(var) for var in variables]
    csv_source[label] = wmdr_codes
    return(csv_source)
