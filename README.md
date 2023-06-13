# oscar-catalogue
Create .xml file based on .csv file to catalogue new facility and / or observations in OSCAR/Surface

**based on https://github.com/joergklausen/oscar-instrument-catalogue**

HOW-TO
1) Clone this github repository and set up a Python environment if you don't have one.
2) Create a .csv or .json file with column names exactly like present in the example files and populate with the facility / observation information. If facility observes several variables, comma-separate them, and make sure entries are properly double-quoted. NB: The correct notation for variables is available from the appropriate code list located at codes.wmo.int/wmdr.
3) Edit the config.yaml file so that paths are as desired.
4) Execute the facility-catalogue.py or observation-catalogue.py script. This should create the XML files according to the .csv file & upload them to OSCAR/Surface (DEPL).
