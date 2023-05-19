#### import ####

import os
import csv
import yaml
import json
import shutil


#### make dictionary  #####

def make_dictionary(label):

    # make dictionary
    reader = csv.reader(open('/home/sdanioth/Documents/git/oscar-catalogue/dictionaries/'+label+'.csv', 'r'))
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


config = "/home/sdanioth/Documents/git/oscar-catalogue/config.yaml"
with open(os.path.abspath(config), "r") as f:
    config = yaml.safe_load(f)
    f.close()

variables = config['variablesWMDR']
variables = config['variablesWMDR_obs']

for var in variables:
    make_dictionary(label=var)
