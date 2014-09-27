#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

file.py

Author: Rodrigo Rega <contacto@rodrigorega.es>
License: CC-BY-SA 3.0 license (http://creativecommons.org/licenses/by/3.0/

"""

import os
import hashlib  # needed to hash md5 and sha1
import zlib  # needed to hash crc32
from lxml import etree  # for xmld validation against dtd file
import datetime  # needed for add timestamp to filenames


class File(object):
    """
    File class
    """

    def __init__(self, path_and_name):
        """
        Class initializer

        Return: None

        :type inputPath: path_and_name
        :param inputPath: full path/filename of the source file
        """
        self.path_and_name = os.path.abspath(path_and_name)
        self.name = os.path.basename(self.path_and_name)
        self.nameNoExtension, self.extension = os.path.splitext(self.name)
        self.path = os.path.dirname(self.path_and_name)
        # size needs to be converted to str...
        self.size = str(os.path.getsize(self.path_and_name))

    name = None
    nameNoExtension = None
    extension = None
    path = None
    path_and_name = None
    size = None
    creationTime = None
    modificationTime = None
    crc = None
    md5 = None
    sha1 = None
    FILE_BLOCK_SIZE_READ = 8192

    def get_hashes(self):
        """
        Calculates file hashes

        Return: None
        """
        with open(self.path_and_name, 'rb') as openedFile:
            self.crc = 0
            self.md5 = hashlib.md5()
            self.sha1 = hashlib.sha1()

            # read first chunk from file
            data = openedFile.read(self.FILE_BLOCK_SIZE_READ)
            while data:  # if there is data in chunk, process it
                self.md5.update(data)
                self.sha1.update(data)
                self.crc = zlib.crc32(data, self.crc)
                # read next chunk from file
                data = openedFile.read(self.FILE_BLOCK_SIZE_READ)
            self.crc = "%X" % (self.crc & 0xFFFFFFFF)
            self.crc = self.crc.lower()
            self.md5 = self.md5.hexdigest()
            self.sha1 = self.sha1.hexdigest()

    def compose_unique_filename(self, path_and_filename, differentiator):
        """
        Checks if a filename exists, if exists returns a unique filename.

        :type path_and_filename: string
        :param path_and_filename: File which will be test if exists.

        :type differentiator: string
        :param differentiator: Can be: "timestamp", "number"

        Return: Unique filename or the 'path_and_filename' unchanged.
        """
        timestamp_format = '%Y-%m-%d-%H-%M-%S'
        path = os.path.dirname(path_and_filename)
        nameNoExtension, extension = os.path.splitext(path_and_filename)

        count = 0
        while os.path.exists(path_and_filename):
            if differentiator is 'timestamp':
                path_and_filename = os.path.join(path, '%s (%s)%s' %
                                                 (nameNoExtension, datetime.datetime.now().strftime(timestamp_format), extension))
            elif differentiator is 'number':
                count += 1
                path_and_filename = os.path.join(path, '%s (%d)%s' %
                                                 (nameNoExtension, count, extension))
            else:
                print('Invalid differentiator')
                sys.exit(2)
        return path_and_filename

    def validate_xml_with_dtd(self, xml_data, dtd_file):
        """
        Validate a xmlfile against a DTD file

        :type xml_data: lxml.objectify.ObjectifiedElement
        :param xml_data: XML data to validate.

        :type dtd_file: string
        :param dtd_file: Full path to .dtd file.

        Return: None if validate is ok. On validate error returns failure info.
        """
        f_dtd = open(dtd_file)
        dtd = etree.DTD(f_dtd)
        f_dtd.close()
        if not dtd.validate(xml_data):
            return dtd.error_log.filter_from_errors()[0]
