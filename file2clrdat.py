#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
file2clrdat.py: Outputs a file in ClrMamePro dat format with rom info (hashes,
size...) from a file or files in a directory. This will speed up the process
of update ClrMamePro .dat files, without using ClrMamePro.

Usage:
  file2clrdat.py INPUT_ROM [-d DAT_FILE]
  file2clrdat.py --help

Arguments:
  INPUT_ROM                           Input rom file o directory with rom files

Options:
  -d DAT_FILE, --datfile=DAT_FILE     Search INPUT_ROM md5 hash in a
                                      ClrMamePro dat file and notify on match
  -h, --help                          Show this help screen.

Output:
  INPUT_ROM_romdata, File with all info from INPUT_ROM
  

Author: Rodrigo Rega <contacto@rodrigorega.es>
License: CC-BY-SA 3.0 license (http://creativecommons.org/licenses/by/3.0/
"""

from __future__ import print_function  # used for print to files
import sys  # needed for get python version and argv
import string  # needed for templating
import os  # needed for file and path manipulations
from file import File  # class for get file data (hashes, size, etc)

from lxml import etree, objectify # for parsinge dat file
import urllib
import pprint

class File2clrdat:
    """
    file2clrdat class
    """

    def __init__(self, inputPath, datFilePath):
        """
        Class initialiser
        
        Return: None
        
        :type inputPath: string
        :param inputPath: file or directory to work with
        
        :type datFilePath: string
        :param datFilePath: work dat file
        """
        self.inputPath = inputPath
        self.datFilePath = datFilePath

    inputPath = None
    datFilePath = None
    fileData = None
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    romTemplateFile = os.path.join(SCRIPT_PATH, 'ClrMamePro_rom_dat.tpl')
    romTemplateContent = None
    romTemplatePopulated = None

    def generateRomData(self):
        """
        Calls functions to acording if input is file or derectory
        
        Return: None
        """
        # TODO: Move inputPath initialiser arg to this function
        if os.path.isfile(self.inputPath):
            self.__processFile()
        elif os.path.isdir(self.inputPath):
            self.__processDirectory()
        else:
            print("Invalid file or directory")
            
    def searchInDatFile(self, search_type, search_content):
        """
        Checks if a given content is insde dat file

        Return: If content was found, returns filename
        """
        with open(self.datFilePath) as f_xml:
            xml_data = f_xml.read()

        datafile = objectify.fromstring(xml_data)
        
        # loop over elements and print their tags and text
        for games in datafile.getchildren():
            for game in games.getchildren():
                if game.get(search_type) == search_content:
                    return game.get("name")

    def __processFile(self):
        """
        Calls all methods to process a file
        
        Return: None
        """
        self.fileData = File(self.inputPath)
        self.fileData.getHashes()
        
        if self.datFilePath:
            romFoundInDatFile = self.searchInDatFile('md5', self.fileData.md5)
            self.__printMatchFoundInDatFile(self.inputPath, romFoundInDatFile)
            confirm = self.__userConfirm('Do you want to generate romdata file anyway? (y or n)')
            if confirm:
                self.__getTemplateContent()
                self.__populateTemplate()
                self.__writePopulatedTemplate()
            else:
                print('Exiting...')
                return
        else:
            # TODO: I dont like this, it is duplicated with previous if...
            self.__getTemplateContent()
            self.__populateTemplate()
            self.__writePopulatedTemplate()
    
    def __userConfirm(self, confirmMsg):
        """get user confirmation to proceed"""
        userChoice = raw_input(confirmMsg)        
        if userChoice == 'y':
            return True
        elif userChoice == 'n':
            return False
        else:
            return self.__userConfirm(confirmMsg)
        
    def __printMatchFoundInDatFile(self, inputRomFile, datFile):
        """ Print msg fom found """
        
        message = """
        Input rom file found in provided dat file:
        - Input rom file: %s
        - Rom name in dat: %s
        """ % (inputRomFile, datFile)

        print(message)


    def __processDirectory(self):
        """
        Calls all methods to process a directory

        Return: None
        """
        for root, dirs, files in os.walk(self.inputPath):
            for file in files:
                self.inputPath = os.path.join(root, file)
                self.__processFile()

    def __getTemplateContent(self):
        """
        Gets content of template file
        
        Return: None
        """
        fRomTemplate = open(self.romTemplateFile)
        self.romTemplateContent = string.Template(fRomTemplate.read())
        fRomTemplate.close()

    def __populateTemplate(self):
        """
        Puts file data inside template
        
        Return: None
        """
        templateDictionary = {
            'gameName': self.fileData.nameNoExtension,
            'romDescription': self.fileData.nameNoExtension,
            'romName': self.fileData.name,
            'romSize': self.fileData.size,
            'romCrc': self.fileData.crc32,
            'romMd5': self.fileData.md5,
            'romSha1': self.fileData.sha1
            }
        self.romTemplatePopulated = (
            self.romTemplateContent.safe_substitute(templateDictionary)
            )

    def __writePopulatedTemplate(self):
        """
        Writes rom data to output file

        Return: None
        """
        fOutput = open(self.fileData.pathAndName + '_romdata', "w")
        print(self.romTemplatePopulated, file=fOutput)
        fOutput.close()


if __name__ == "__main__":
    """
    Main
    
    Return: None
    """
    # check Python version
    major, minor, micro, releaselevel, serial = sys.version_info
    if (major, minor) < (2, 7):
        print('You must use Python 2,7 or higher')
        sys.exit(2)

    try:
        from docopt import docopt
    except:
        print ("""
        Please install docopt using:
            pip install docopt
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise
        
    args = docopt(__doc__, version='1.0.0rc2')
    
    file2clrdat = File2clrdat(args['INPUT_ROM'],args['--datfile'])
    file2clrdat.generateRomData()
