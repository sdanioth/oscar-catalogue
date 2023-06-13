#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import
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
import io
from pyoscar import OSCARClient
import dateutil.parser
from dictionaries_getWMDRnotation import get_WMDR_notation



class ObservationCatalogue:
    """
    Read flat file, convert to WMDR XML file, upload to OSCAR/Surface.

    Read flat file containing facility catalogue entries,
    convert to WMDR XML file, upload to OSCAR/Surface.
    """

    @classmethod
    def __init__(self, config):
        """
        Constructor

        Parameters
        ----------
        config : str
            Full path to configuration file.

        Returns
        -------
        None.

        """
        try:
            with open(os.path.abspath(config), "r") as f:
                config = yaml.safe_load(f)
                f.close()

            # setup logging
            for h in logging.root.handlers[:]:
                logging.root.removeHandler(h)
            logdir = os.path.expanduser(config['logging'])
            os.makedirs(logdir, exist_ok=True)
            logfile = '%s.log' % time.strftime('%Y%m%d')
            self.logfile = os.path.join(logdir, logfile)
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%y-%m-%d %H:%M:%S',
                                filename=str(self.logfile),
                                filemode='a')

            self.source = os.path.expanduser(config['ObservationSource'])
            self.target = os.path.expanduser(config['ObervatonTarget'])
            self.template = config['ObservationTemplate']
            self.variablesWMDR_obs = config['variablesWMDR_obs']
            self.header = { 'dtm': time.strftime("%Y-%m-%dT%H:%M:%S"),
                    'individualName': config['individualName'],
                            'organisationName': config['organisationName'],
                            'electronicMailAddress': config['organisationName'] }

            self.upload = config['upload']
            self.proxies = config['proxies']
            self.token = config['token']
            self.variablesWMDR_obs = config['variablesWMDR_obs']
            url = self.upload
            token = self.token


        except Exception as err:
            self.logger.error('Error setting up FacilityCatalogue', err)



    @classmethod
    def csv2wmdr(self, verbose=True):
        """
        Read a flat CSV file, cast to WMDR XML file, save as target

        Parameters
        ----------
        verbose : bln, optional
            Should log file be written? The default is True.

        Returns
        -------
        filename with full path.

        """
        try:
            sanitize = lambda x: html.escape(x) if len(x) > 0 else 'unknown'

            # read jinja template
            templateLoader = jinja2.FileSystemLoader(searchpath="./")
            templateEnv = jinja2.Environment(loader=templateLoader)
            template = templateEnv.get_template(self.template)

            # read source file and convert to list of dictionaries, one for
            # each combination of manufacturer, model, variable
            with open(self.source) as f:
                reader = csv.DictReader( f )
                files = []
                for row in reader:
                    var = 'ObservedVariableAtmosphere'
                    d1 = { key: sanitize(row[key]) for key in row.keys() if key != var }
                    for ele in row[var].split(','):
                        observation = {var: ele.strip(), 'uuid': uuid.uuid4()}
                        observation.update(d1)

                        # date in correct format (YYYY-MM-DD)
                        #print("obs1:", observation)
                        observation['beginPositionDataGeneration'] = dateutil.parser.parse(observation['beginPositionDataGeneration'],fuzzy=True).date()

                        # get WMDR Codes Register notation
                        for var in self.variablesWMDR_obs:
                            observation = get_WMDR_notation(source=observation,label=var)
                        #print("obs2:", observation)

                        # generate XML file
                        xml = template.render(header=self.header, observation=observation)
                        file = os.path.join(self.target, "%s %s .xml" % (observation['WIGOSstationIdentifier'], observation['ObservedVariableAtmosphere'][0]))
                        file = file.replace(" ", "_")
                        files.append(file)
                        with open(file, 'w') as f:
                            f.write(xml)
                            f.close()
                        if verbose:
                            self.logger.info("XML file saved to " + file)

            return(files)

        except Exception as err:
            self.logger.error(err)
            return(err)



if __name__ == '__main__':
    config = os.path.join(os.getcwd(), 'config.yaml')
    observation_catalogue = ObservationCatalogue(config)
    xml_files = observation_catalogue.csv2wmdr()

    with open(os.path.abspath(config), "r") as f:
        config = yaml.safe_load(f)
        f.close()
    for xml_file in xml_files:
        with open(xml_file) as r:
            client = OSCARClient(api_token=config['token'])
            xml = r.read()
            response = client.upload(xml)
            print(response)
