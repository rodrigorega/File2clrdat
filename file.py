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
