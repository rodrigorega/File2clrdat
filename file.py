#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  file.py
#
# Author: Rodrigo Rega <contacto@rodrigorega.es>
# License: CC-BY-SA 3.0 license (http://creativecommons.org/licenses/by/3.0/
#

import os
import hashlib  # needed to hash md5 and sha1
import zlib  # neeeded to hash crc32


class File():
    """
    File class
    """

    def __init__(self, pathAndName):
        """
        Class initialiser
        
        Return: None

        :type inputPath: pathAndName
        :param inputPath: full path/filename of the source file
        """
        self.pathAndName = os.path.abspath(pathAndName)
        self.name = os.path.basename(self.pathAndName)
        self.nameNoExtension = os.path.splitext(self.name)[0]
        self.path = os.path.dirname(self.pathAndName)
        # size needs to be converted to str...
        self.size = str(os.path.getsize(self.pathAndName))

    name = None
    nameNoExtension = None
    path = None
    pathAndName = None
    size = None
    creationTime = None
    modificationTime = None
    crc32 = None
    md5 = None
    sha1 = None
    FILE_BLOCK_SIZE_READ = 8192

    def getHashes(self):
        """
        Calculates file hashes
        
        Return: None
        """
        with open(self.pathAndName, 'rb') as openedFile:
            self.crc32 = 0
            self.md5 = hashlib.md5()
            self.sha1 = hashlib.sha1()

            # read first chunk from file
            data = openedFile.read(self.FILE_BLOCK_SIZE_READ)
            while data:  # if there is data in chunk, process it
                self.md5.update(data)
                self.sha1.update(data)
                self.crc32 = zlib.crc32(data, self.crc32)
                # read next chunk from file
                data = openedFile.read(self.FILE_BLOCK_SIZE_READ)
            self.crc32 = "%X" % (self.crc32 & 0xFFFFFFFF)
            self.crc32 = self.crc32.lower()
            self.md5 = self.md5.hexdigest()
            self.sha1 = self.sha1.hexdigest()
