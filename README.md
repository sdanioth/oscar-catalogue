# oscar-instrument-catalogue
Create XML file to expand or update the OSCAR/Surface Instrument Catalogue

HOW-TO
1) Clone this github repository and set up a Python environment if you don't have one.
2) Create a .csv file with column names exactly like present in the example file and populate with the instrument information. If an instrument can be used to observe several variables, comma-separate them, and make sure entries are properly double-quoted. NB: The correct notation for variables is available from the appropriate code list located at codes.wmo.int/wmdr.
3) Edit the config.yaml file so that paths are as desired.
4) Execute the instrument-catalogue.py script. This should create and upload the XML files according to the .csv file.

You can try to [![Run on Repl.it](https://repl.it/badge/github/joergklausen/oscar-instrument-catalogue)](https://repl.it/github/joergklausen/oscar-instrument-catalogue) ... I didn't succeed myself, but I might have missed some configuration requirements.
