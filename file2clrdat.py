#!/usr/bin/env python
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
import sys
import string  # needed for templating
import os

from file import File


def _main():
    """
    Main...
    """
    global scriptPath
    global errorCode
    errorCode = 0
    errorCodes = (
        'No error',  # error000
        'Use: python file2clrdat.py FILE_OR_DIRECTORY',  # error001
        'Invalid file or directory',  # error002
        )

    scriptPath = os.path.dirname(os.path.realpath(__file__))

    _argsCheck()  # check if we have correct arguments
    if not errorCode:  # if no error continue
        readInputWriteOutput(sys.argv[1])

    if errorCode:
        print('- Error:', errorCodes[errorCode])
        sys.exit(errorCode)


def _argsCheck():
    """
    Validate arguments passed to the script, return 0 is no error
    """
    global errorCode

    if len(sys.argv) != 2:
        errorCode = 1


def readInputWriteOutput(inputPath):
    """
    Calls functions to read input and write output file
    """
    global errorCode

    if os.path.isfile(inputPath):
        objFile = File(inputPath)
        objFile.getHashes()
        writeRomDataToFile(objFile)
    else:
        if os.path.isdir(inputPath):
            inputPath = os.path.abspath(inputPath)

            files = [
                f for f in os.listdir(inputPath)
                if os.path.isfile(
                    os.path.join(inputPath, os.path.basename(f))
                    )
                ]
            for file in files:
                objFile = File(os.path.join(inputPath, file))
                objFile.getHashes()
                writeRomDataToFile(objFile)
        else:
            errorCode = 2


def writeRomDataToFile(objFile):
    """
    Writes rom data to final file
    """
    templateDictionary = {
        'gameName': objFile.nameNoExtension,
        'romDescription': objFile.nameNoExtension,
        'romName': objFile.name,
        'romSize': objFile.size,
        'romCrc': objFile.crc32,
        'romMd5': objFile.md5,
        'romSha1': objFile.sha1
        }

    # get template file
    fileRomTemplate = open(os.path.join(scriptPath, 'ClrMamePro_rom_dat.tpl'))
    templateSrc = string.Template(fileRomTemplate.read())
    fileRomTemplate.close()

    # write to output file template and data
    templateWithData = templateSrc.safe_substitute(templateDictionary)
    f = open(objFile.pathAndName + '_romdata', "w")
    print(templateWithData, file=f)
    f.close()


if __name__ == "__main__":
    # check Python version
    major, minor, micro, releaselevel, serial = sys.version_info
    if (major, minor) < (2, 7):
        print('You must use Python 2,7 or higher')
        sys.exit(2)

    _main()
