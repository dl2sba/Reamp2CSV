import struct
import csv
import locale
import sys
import os
from datetime import datetime
from datetime import timezone

print("*********************************************************************************")
print("***                                                                           ***")
print("*** simple REAMP logger file converter to CSV         Version 1.0             ***")
print("***                                                                           ***")
print("*** (c) Dietmar Krause, DL2SBA 2026                   2026-02-20              ***")
print("***                                                                           ***")
print("*** Usage                                                                     ***")
print("***      python scriptName <parm1> <parm2> <parm3>                            ***")
print("***                                                                           ***")
print("***      parm1    locale used for number formatting                           ***")
print("***               'German' for ',' as decimal seperator                       ***")
print("***               'US' for '.' as decimal seperator                           ***")
print("***      parm2    Input filename in *.reamp format                            ***")
print("***      parm3    Output filename in CSV-format                               ***")
print("***               Field seperator is ';'                                      ***")
print("***               Field#                                                      ***")
print("***               1   relative time in µs to start of recording               ***")
print("***               2   absolute time of recording in UTC                       ***")
print("***                   the time is fully qualifier down to µs                  ***")
print("***               3   first channel in file                                   ***")
print("***               4   second channel in file (optional)                       ***")
print("***               5   third channel in file (optional)                        ***")
print("***                                                                           ***")
print("***               voltage data is written in mV                               ***")
print("***               current data is written in µA                               ***")
print("***                                                                           ***")
print("***  Restrictions:                                                            ***")
print("***      ChannelMap is not used                                               ***")
print("***                                                                           ***")
print("***  Import into Excel                                                        ***")
print("***      The timestamp in the file is down to µs resolution.                  ***")
print("***      Excel currently supports only ms resolution for timestamps           ***")
print("***      To see at least ms in the column, use the custom cell format         ***")
print("***                'TT.MM.JJJJ hh:mm:ss,000'                                  ***")
print("***                                                                           ***")
print("***  Send comments and bug reports to 'labview@dl2sba.de'                     ***")
print("***                                                                           ***")
print("*********************************************************************************")

if len(sys.argv) < 4:
    print("Incorrect usage")
    sys.exit(-1)

locale2use = sys.argv[1]
inputFilename = sys.argv[2]
outputFilename = sys.argv[3]

numChannels = 0
locale.setlocale(locale.LC_ALL, locale2use) 

with open(inputFilename, 'rb') as f:
    binary_content = f.read(0x200) 

    fileVersion         = struct.unpack('<h', binary_content[0:2])[0]
    fileHeaderSize      = struct.unpack('<h', binary_content[2:4])[0]
    fileChannelCount    = struct.unpack('B', binary_content[8:9])[0]
    fileChannelMap      = struct.unpack('B', binary_content[9:10])[0]
    fileSampleTime      = struct.unpack('<h', binary_content[10:12])[0] / 10 # in ms ticks
    fileType            = struct.unpack('B', binary_content[8:9])[0]
    fileStartTS         = struct.unpack('<Q', binary_content[0x1f8:0x200])[0] / 1000


    print("fileVersion......", fileVersion)
    print("fileHeaderSize...", fileHeaderSize)
    print("fileChannelCount.",fileChannelCount)
    print("fileChannelMap...",fileChannelMap)
    print("fileSampleTime...",fileSampleTime,"ms")
    print("fileType.........",fileType)
    print("fileStartTS......",datetime.fromtimestamp(fileStartTS, tz=timezone.utc),fileStartTS, "s")
    print("Input filename...", inputFilename)
    print("Output filename..", outputFilename)
    print("Output locale....", locale2use)

    with open(outputFilename, "w", newline="", encoding="utf-8") as outFile:
        writer = csv.writer(outFile, delimiter=";")
        writer.writerow(["time rel", "time abs", "channel 0", "channel 1", "channel 2"])

        #   detector for end of file
        #   increments are in ms
        lastIncrement = -1
        increment = 0
        bytesPerChannel = (fileChannelCount + 1 ) * 8
        timestampFromIncrement = ""
        numSamples = 0
        #
        #   read the data lines
        while True:
            valueArray = []
            #   read all data of a sample
            sampleRaw = f.read(bytesPerChannel)
            #   read 8 byte double value
            doubleIncrement = struct.unpack('<d', sampleRaw[0:8])[0]
            #   convert to ms
            increment = doubleIncrement
            #print(increment)
            if ( increment == lastIncrement):
                break
            else:
                lastIncrement = increment
            incrementLocal = locale.format_string("%f", increment)
            valueArray.append(incrementLocal)

            #   timestamp of current sample in ms
            sampleTime = fileStartTS + increment
            timestampFromIncrement = datetime.fromtimestamp(sampleTime, tz=timezone.utc)
            #print(sampleTime, timestampFromIncrement)
            valueArray.append(timestampFromIncrement)

            for chanNo in range(fileChannelCount):
                startIdx = chanNo * 8 + 8
                stopIdx  = startIdx + 8
                chanVal = struct.unpack('<d', sampleRaw[startIdx:stopIdx])[0]
                chanValLocale = locale.format_string("%f", chanVal)
                valueArray.append(chanValLocale)
            writer.writerow(valueArray)
            numSamples += 1

    print("fileLastTS.......", timestampFromIncrement)
    print("samples written..", numSamples)
    print("bye ...")