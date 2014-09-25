#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
file2clrdat.py: Outputs a file in ClrMamePro dat format with rom info (hashes,
size...) from a file or files in a directory. This will speed up the process
of update ClrMamePro .dat files, without using ClrMamePro.

Usage:
  file2clrdat.py INPUT_ROM
  file2clrdat.py INPUT_ROM [(-s SEARCH_TYPE -d DAT_FILE)]
  file2clrdat.py --help

Arguments:
  INPUT_ROM                           Input rom file o directory with rom files

Options:
  -s SEARCH_TYPE, --searchtype=type   Search inside a dat file for a type of
                                      value wich match with INPUT_ROM. Accepted
                                      "type" values: size, crc32, md5, sha1
                                      Must be used with "-d" option.
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
from lxml import objectify  # for parsinge dat file


class File2clrdat(object):
    """
    file2clrdat class
    """

    def __init__(self, input_path, datfile_path, search_type):
        """
        Class initialiser

        Return: None

        :type input_path: string
        :param input_path: file or directory to work with

        :type datfile_path: string
        :param datfile_path: work dat file

        :type search_type: string
        :param search_type: value that will be searched in dat file
        """
        self.input_path = input_path
        self.datfile_path = datfile_path
        self.search_type = search_type

    input_path = None
    search_type = None
    datfile_path = None
    file_data = None
    VALID_SEARCH_TYPES = ['size', 'md5', 'crc32', 'sha1']
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    rom_template_file = os.path.join(SCRIPT_PATH, 'ClrMamePro_rom_dat.tpl')
    rom_template_content = None
    rom_template_populated = None

    def generate_rom_data(self):
        """
        Calls functions to acording if input is file or derectory

        Return: None
        """
        # TODO: Move input_path initialiser arg to this function
        if os.path.isfile(self.input_path):
            self.__process_file()
        elif os.path.isdir(self.input_path):
            self.__process_directory()
        else:
            print("Invalid file or directory")

    def search_in_datfile(self, search_type, search_content):
        """
        Checks if a given content is insde dat file

        Return: If content was found, returns filename

        :type search_type: string
        :param search_type: Type of search (md5, size, crc...)

        :type search_content: string
        :param search_content: Content that will be matched
        """
        if search_type == "crc32":
            search_type = "crc"  # I need this to match with File class

        with open(self.datfile_path) as f_xml:
            xml_data = f_xml.read()

        datafile = objectify.fromstring(xml_data)

        # loop over elements and print their tags and text
        for games in datafile.getchildren():
            for game in games.getchildren():
                if game.get(search_type) == search_content:
                    return game.get("name")

    def __process_file(self):
        """
        Calls all methods to process a file

        Return: None
        """
        self.file_data = File(self.input_path)
        self.file_data.get_hashes()

        if self.datfile_path:
            rom_found_in_datfile = self.search_in_datfile(
                self.search_type, getattr(self.file_data, self.search_type))
            if rom_found_in_datfile:
                self.__print_match_found_in_datfile(
                    self.input_path, rom_found_in_datfile)
                confirm = self.__user_confirm(
                    'Do you want to generate romdata file anyway? (y or n)')
                if confirm is not True:
                    print('Ignoring file...')
                    return

        self.__get_template_content()
        self.__populate_template()
        self.__write_populated_template()

    def __user_confirm(self, confirm_msg):
        """
        Get user confirmation to proceed

        Return: True if user confirmed, False if not
        """
        user_choice = raw_input(confirm_msg)
        if user_choice == 'y':
            return True
        elif user_choice == 'n':
            return False
        else:
            return self.__user_confirm(confirm_msg)

    def __print_match_found_in_datfile(self, input_romfile,
                                       rom_found_in_datfile):
        """
        Print found match msg

        Return: None

        :type input_romfile: string
        :param input_romfile: Input file

        :type rom_found_in_datfile: string
        :param rom_found_in_datfile: Rom matched in datfile
        """
        message = """
        Input rom file found in provided dat file:
        - Input rom file: %s
        - Rom name in dat: %s
        """ % (input_romfile, rom_found_in_datfile)

        print(message)

    def __process_directory(self):
        """
        Calls all methods to process a directory

        Return: None
        """
        for root, dirs, files in os.walk(self.input_path):
            for thisfile in files:
                self.input_path = os.path.join(root, thisfile)
                self.__process_file()

    def __get_template_content(self):
        """
        Gets content of template file

        Return: None
        """
        f_rom_template = open(self.rom_template_file)
        self.rom_template_content = string.Template(f_rom_template.read())
        f_rom_template.close()

    def __populate_template(self):
        """
        Puts file data inside template

        Return: None
        """
        template_dictionary = {
            'gameName': self.file_data.nameNoExtension,
            'romDescription': self.file_data.nameNoExtension,
            'romName': self.file_data.name,
            'romSize': self.file_data.size,
            'romCrc': self.file_data.crc32,
            'romMd5': self.file_data.md5,
            'romSha1': self.file_data.sha1
            }
        self.rom_template_populated = (
            self.rom_template_content.safe_substitute(template_dictionary)
            )

    def __write_populated_template(self):
        """
        Writes rom data to output file

        Return: None
        """
        f_output = open(self.file_data.path_and_name + '_romdata', "w")
        print(self.rom_template_populated, file=f_output)
        f_output.close()


if __name__ == "__main__":
    """
    Main

    Return: None
    """
    # check Python version
    MAJOR, MINOR, MICRO, RELEASELEVEL, SERIAL = sys.version_info
    if (MAJOR, MINOR) < (2, 7):
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

    ARGS = docopt(__doc__, version='1.0.0rc2')

    MY_FILE2CLRDAT = File2clrdat(
        ARGS['INPUT_ROM'], ARGS['--datfile'], ARGS['--searchtype'])
    if ARGS['--searchtype'] in MY_FILE2CLRDAT.VALID_SEARCH_TYPES:
        MY_FILE2CLRDAT.generate_rom_data()
    else:
        print('- %s is not a valid search type. Use --help to more info.'
              % ARGS['--searchtype'])
