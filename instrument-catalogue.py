#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:42:37 2019

@author: joerg.klausen@alumni.ethz.ch
"""

import os
import logging
import time
import csv
import html
import jinja2
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import uuid
import yaml


class InstrumentCatalogue:
    """
    Read flat file, convert to WMDR XML file, upload to OSCAR/Surface.

    Read flat file containing instrument catalogue entries, 
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
            
            self.source = os.path.expanduser(config['source'])
            self.target = os.path.expanduser(config['target'])
            self.template = config['template'] 
            self.header = { 'dtm': time.strftime("%Y-%m-%dT%H:%M:%S"), 
                    'individualName': config['individualName'],
                            'organisationName': config['organisationName'],
                            'electronicMailAddress': config['organisationName'] }

            self.upload = config['upload']
            self.proxies = config['proxies']
            self.token = config['token']
            
        except Exception as err:
            self.logger.error('Error setting up InstrumentCatalogue', err)



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
                    var = 'observedVariable'
                    d1 = { key: sanitize(row[key]) for key in row.keys() if key != var }
                    for ele in row[var].split(','):
                        instrument = {var: ele.strip(), 'uuid': uuid.uuid1()} 
                        instrument.update(d1)
                                   
                        # generate XML file
                        xml = template.render(header=self.header, instrument=instrument)
                        file = os.path.join(self.target, "%s %s %s.xml" % (instrument['manufacturer'], instrument['model'], instrument['observedVariable']))
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
        
        
    def upload_wmdr(self, wmdr_file: str, verbose=True) -> str:
        """
        Upload WMDR XML using the OSCAR/Surface API.

        Upload a WMDR XML file using the OSCAR/Surface API.

        Parameters
        ----------
        wmdr_file : str
            Qualified path to WMDR XML file
        verbose : bln
            should a logger be invoked? defaults to True

        Returns
        -------
        str
            http response code (200 if successful), error message otherwise
        """
        try:
            url = self.upload
            token = self.token
            headers = {'X-WMO-WMDR-Token': token,
                       'content-type': 'text/xml'}
            msg = "Uploading XML file " + wmdr_file + " ... "
            if verbose:
                logger = logging.getLogger(__name__)
                logger.info(msg)

            with requests.Session() as session:
                logging.getLogger("urllib3").setLevel(logging.WARNING)
                retries = Retry(total=5,
                                backoff_factor=0.3,
                                status_forcelist=[500, 502, 503, 504])
                session.mount('http://', HTTPAdapter(max_retries=retries))
                session.mount('https://', HTTPAdapter(max_retries=retries))

            with open(wmdr_file, 'r') as data:
                response = session.post(url,
                                        proxies=self.proxies, 
                                        data=data.read(), 
                                        headers=headers)

                msg = str(response.content)

                if response.status_code == 200:
                    if verbose:
                        logger.info(msg)
                else:
                    msg += "; token: " + str(token)
                    if verbose:
                        logger.warning(msg)

                session.close()

            return(response.status_code)

        except requests.exceptions.HTTPError as err:
            logger.error("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            logger.error("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            logger.error("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            logger.error("OOps: Something Else", err)
        

if __name__ == '__main__':
    config = os.path.join(os.getcwd(), 'config.yaml')
    instrument_catalogue = InstrumentCatalogue(config)
    xml_files = instrument_catalogue.csv2wmdr()
    for xml_file in xml_files:
        response = instrument_catalogue.upload_wmdr(xml_file)
        print(response)