#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
file2clrdat.py: Outputs a file in ClrMamePro dat format with rom info (hashes,
size...) from a file or files in a directory. This will speed up the process
of update ClrMamePro .dat files, without using ClrMamePro.

Usage:
  file2clrdat.py INPUT_ROM
  file2clrdat.py INPUT_ROM [(-s SEARCH_TYPE -d DAT_FILE [-m DIR] [-u DIR])]
  file2clrdat.py --help

Arguments:
  INPUT_ROM                            Input rom file o directory with roms.

Options:
  -s SEARCH_TYPE, --searchtype=type    Search inside a dat file for a type of
                                       value to match with INPUT_ROM. Accepted
                                       "type" values: size, crc, md5, sha1
                                       Must be used with "-d" option.
  -d DAT_FILE, --datfile=DAT_FILE      File that will be searched, type of
                                       search is given with "-s" option.
                                       Must be used with "-s" option.
  -m MATCHED_DIR, --matcheddir=DIR     INPUT_ROM will be moved to MATCHED_DIR
                                       if exists in DAT_FILE.
                                       Must be used with "-sd" options.
  -u UNMATCHED_DIR --unmatcheddir=DIR  INPUT_ROM will be moved to UNMATCHED_DIR
                                       if not exists in DAT_FILE.
                                       Must be used with "-sd" options.
  -h, --help                           Show this help screen.

Output:
  INPUT_ROM_romdata, File with all info from INPUT_ROM
  Optional: Move scanned roms to folders.

Examples:
  - Generate rom info (rom.bin_rondata) from a single rom file:
      file2clrdat.py "c:\my_downloads\rom.bin"

  - Scan a directory, match sha1 hashes of every file in that directory with
    a dat file, matched files will be moved to "dupe_roms" directory, files not
    found in dat file will be moved to "new_roms" directory adding a file with
    rom data for every file:
      file2clrdat.py "c:\my_downloaded_roms" -s sha1 -d "c:\my_dat_wip\my_dat.dat" -m "c:\my_dat_wip\dupe_roms" -u "c:\my_dat_wip\new_roms"

Author: Rodrigo Rega <contacto@rodrigorega.es>
License: CC-BY-SA 3.0 license (http://creativecommons.org/licenses/by/3.0/
"""

from __future__ import print_function  # used for print to files
import sys  # needed for get python version and argv
import string  # needed for templating
import os  # needed for file and path manipulations
from file import File  # class for get file data (hashes, size, etc)
from lxml import objectify  # for parsing dat file


class File2clrdat(object):
    """
    file2clrdat class
    """

    def __init__(self, input_path, datfile_path,
                 search_type, matched_dir, unmatched_dir):
        """
        Class initializer

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
        self.matched_dir = matched_dir
        self.unmatched_dir = unmatched_dir

    input_path = None
    search_type = None
    datfile_path = None
    matched_dir = None
    unmatched_dir = None
    file_data = None
    VALID_SEARCH_TYPES = ['size', 'md5', 'crc', 'sha1']
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    rom_template_file = os.path.join(SCRIPT_PATH, 'ClrMamePro_rom_dat.tpl')
    rom_template_content = None
    rom_template_populated = None

    def generate_rom_data(self):
        """
        Calls functions to according if input is file or directory

        Return: None
        """
        # TODO: Move input_path initializer arg to this function
        if os.path.isfile(self.input_path):
            self.__process_file()
        elif os.path.isdir(self.input_path):
            self.__process_directory()
        else:
            print("Invalid file or directory")

    def search_in_datfile(self, search_type, search_content):
        """
        Checks if a given content is inside dat file

        Return: If content was found, returns filename

        :type search_type: string
        :param search_type: Type of search (md5, size, crc...)

        :type search_content: string
        :param search_content: Content that will be matched
        """
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
                self.__print_match_found_in_datfile(rom_found_in_datfile)
                if self.matched_dir:
                    self._move_file(self.matched_dir)
            else:
                if self.unmatched_dir:
                    self._move_file(self.unmatched_dir)
                self.__get_template_content()
                self.__populate_template()
                self.__write_populated_template()
        else:
            self.__get_template_content()
            self.__populate_template()
            self.__write_populated_template()   

    def _move_file(self, destination_dir):
        """
        Move rom file to a given directory. If exists it will be renamed.

        Return: None

        :type destination_dir: string
        :param destination_dir: Directory where file will be moved
        """
        destination_file = os.path.join(destination_dir, self.file_data.name)
        count = 0
        while os.path.exists(destination_file):
            count += 1
            destination_file = os.path.join(destination_dir, '%s (%d) %s' %
                                            (self.file_data.nameNoExtension,
                                             count, self.file_data.extension))
        os.rename(self.input_path, destination_file)

    def __print_match_found_in_datfile(self, rom_found_in_datfile):
        """
        Print found match message

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
        """ % (self.input_path, rom_found_in_datfile)

        print(message)

    def __process_directory_recursive(self):
        """
        Calls all methods to process a directory and all subdirectories

        Return: None
        """
        for root, dirs, files in os.walk(self.input_path):
            for thisfile in files:
                self.input_path = os.path.join(root, thisfile)
                self.__process_file()

    def __process_directory(self):
        """
        Calls all methods to process a directory

        Return: None
        """
        path = self.input_path

        for thisfile in os.listdir(path):
            path_and_file = os.path.join(path, thisfile)
            if os.path.isfile(path_and_file):
                self.input_path = path_and_file
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
            'romCrc': self.file_data.crc,
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
        if self.unmatched_dir:
            dst_dir = self.unmatched_dir
        else:
            dst_dir = self.file_data.path

        romdata_file = os.path.join(dst_dir, self.file_data.name + '_romdata')
        f_output = open(romdata_file, "w")
        print(self.rom_template_populated, file=f_output)
        f_output.close()


def _validate_python_version():
    '''
    Check Python version

    Return: None
    '''
    MAJOR, MINOR, MICRO, RELEASELEVEL, SERIAL = sys.version_info
    if (MAJOR, MINOR) < (2, 7):
        print('You must use Python 2,7 or higher')
        sys.exit(2)

if __name__ == "__main__":
    """
    Main

    Return: None
    """
    _validate_python_version()

    try:
        from docopt import docopt
    except:
        print ("""
        Please install docopt using:
            pip install docopt
        For more info refer to: https://github.com/docopt/docopt
        """)
        raise

    ARGS = docopt(__doc__, version='1.0.0rc2')
    MY_FILE2CLRDAT = File2clrdat(
        ARGS['INPUT_ROM'], ARGS['--datfile'], ARGS['--searchtype'],
        ARGS['--matcheddir'], ARGS['--unmatcheddir'])

    if ARGS['--matcheddir'] and ARGS['--unmatcheddir']:
        if ARGS['--matcheddir'] == ARGS['--unmatcheddir']:
            print ('MATCHED_DIR and UNMATCHED_DIR must be different.')
            sys.exit(3)

    if ARGS['--searchtype']:
        if not ARGS['--searchtype'] in MY_FILE2CLRDAT.VALID_SEARCH_TYPES:
            print('- %s is not a valid search type. Use --help to more info.'
                  % ARGS['--searchtype'])
            sys.exit(4)
    MY_FILE2CLRDAT.generate_rom_data()