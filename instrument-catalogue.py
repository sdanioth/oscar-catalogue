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

            # read source file and convert to list of dictionaries, one for
            # each instrument
            instruments = []
            with open(self.source) as f:
                reader = csv.DictReader( f  )
                for row in reader:
                    var = 'observedVariable'
                    d1 = { key: sanitize(row[key]) for key in row.keys() if key != var }
                    for ele in row[var].split(','):
                        d2 = {var: ele.strip(), 'uuid': uuid.uuid1()} 
                        d2.update(d1)
                        instruments.append(d2)
                                   
            # read jinja template
            templateLoader = jinja2.FileSystemLoader(searchpath="./")
            templateEnv = jinja2.Environment(loader=templateLoader)
            template = templateEnv.get_template(self.template)

            # generate XML file
            xml = template.render(header=self.header, instruments=instruments)

            with open(self.target, 'w') as f:
                f.write(xml)
                f.close()
            if verbose:
                self.logger.info("XML file saved to " + self.target)
                
            return()

        except Exception as err:
            self.logger.error(err)
            return(err)
        

if __name__ == '__main__':
    config = os.path.join(os.getcwd(), 'config.yaml')
    instrument_catalogue = InstrumentCatalogue(config)
    instrument_catalogue.csv2wmdr()
    