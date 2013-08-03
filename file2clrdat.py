#!/usr/bin/env python
"""
This Python script generates "line rom" info from a single file.
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
import sys
import hashlib  # needed to hash md5 and sha1
import zlib  # neeeded to hash crc32
import string  # needed for templating
import os  # needed to get size of files


def main():
    """
    Main...
    """
    errorCodes = (
        'No error',  # error000
        'Use python file2clrdat.py file',  # error001
        'Invalid file',  # error001
        )

    validateArgsReturn = validateArgs()  # check if we have correct arguments
    if validateArgsReturn == 0:  # if no error continue
        fileToHash = sys.argv[1]
        crc, md5, sha1 = getFileHashes(fileToHash)
        writeRomDataToFile(
            fileToHash, os.path.getsize(fileToHash), crc, md5, sha1
            )
    else:
        print('- Error:', errorCodes[validateArgsReturn])
        sys.exit(1)


def validateArgs():
    """
    Validate arguments passed to the script, return 0 is no error
    """
    if len(sys.argv) != 2:
        return(1)
    if not os.path.isfile(sys.argv[1]):  # if not exists or is not a file
        return(2)
    else:
        return(0)


def getFileHashes(filePath):
    """
    Calculates hashes and return them
    """
    BUFFER_SIZE = 8192  # we will process file in chunks of this size
    crc = 0

    with open(filePath, 'rb') as openedFile:
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()

        data = openedFile.read(BUFFER_SIZE)  # read first chunk from file
        while data:  # if there is data in chunk, process it
            md5.update(data)
            sha1.update(data)
            crc = zlib.crc32(data, crc)
            data = openedFile.read(BUFFER_SIZE)  # read next chunk from file

        return ("%X" % (crc & 0xFFFFFFFF), md5.hexdigest(), sha1.hexdigest())


def writeRomDataToFile(fileToHash, size, crc, md5, sha1):
    """
    Writes rom data to finla file
    """
    templateDictionary = {
        'gameName': fileToHash,
        'romDescription': fileToHash,
        'romName': fileToHash,
        'romSize': size,
        'romCrc': crc.lower(),
        'romMd5': md5,
        'romSha1': sha1
        }

    # get template file
    fileRomTemplate = open('ClrMamePro_rom_dat.tpl')
    templateSrc = string.Template(fileRomTemplate.read())
    fileRomTemplate.close()

    # write to output file template and data
    templateWithData = templateSrc.safe_substitute(templateDictionary)
    f = open(fileToHash + '_romdata', "w")
    print(templateWithData, file=f)
    f.close()


if __name__ == "__main__":
    # check Python version
    major, minor, micro, releaselevel, serial = sys.version_info
    if (major, minor) < (2, 7):
        print('You must use Python 2,7 or higher')
        sys.exit(2)

    main()
