#### import ####

import os
import logging
import time
import csv
import html
import jinja2
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import uuid
import yaml
import requests
import io
import json
import re
import shutil


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


#### make dictionary  #####

def make_dictionary(WMDR_csv, label):

    # make dictionary
    reader = csv.reader(open('/home/sdanioth/Documents/git/oscar-catalogue/'+WMDR_csv, 'r'))
    dictionary = {}
    for row in reader:
        k, v = row
        dictionary[k] = v

    # save dictionary as .json file
    filename = label+"_dictionary.json"
    with open(filename, 'w') as f:
        f.write(json.dumps(dictionary))

    # move dictionary to dictionaries folder
    shutil.move(filename, os.getcwd()+'/dictionaries/'+filename)

#make_dictionary(WMDR_csv='ObservedVariableAtmosphere_WMDR.csv', label="ObservedVariableAtmosphere")
