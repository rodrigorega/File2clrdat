#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This Python script generates "line rom" info from a file or files in a dir.
This info can be added manually to a ClrMamePro .dat.

Generates one file with rom data from a sngle file. This data can be
merged in a existing ClrMamePro .dat file.
I use this to speed up the process of update my .dat files, without using
ClrMamePro.

Author: Rodrigo Rega <contacto@rodrigorega.es>
License: CC-BY-SA 3.0 license (http://creativecommons.org/licenses/by/3.0/

Use: file2clrdat filename.rom
Output: filename.rom_romdata
"""

from __future__ import print_function  # used for print to files
import sys  # needed for get python version and argv
import string  # needed for templating
import os  # needed for file and path manipulations
from file import File  # class for get file data (hashes, size, etc)


class File2clrdat:
    """
    file2clrdat class
    """

    def __init__(self, inputPath):
        """
        Class initialiser
        
        Return: None
        
        :type inputPath: string
        :param inputPath: file or directory to work with
        """
        self.inputPath = inputPath

    inputPath = None
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

    def __processFile(self):
        """
        Calls all methods to process a file
        
        Return: None
        """
        self.fileData = File(self.inputPath)
        self.fileData.getHashes()

        self.__getTemplateContent()
        self.__populateTemplate()
        self.__writePopulatedTemplate()

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

    if len(sys.argv) != 2:
        print("Use: python file2clrdat.py FILE_OR_DIRECTORY")
    else:
        file2clrdat = File2clrdat(sys.argv[1])
        file2clrdat.generateRomData()
