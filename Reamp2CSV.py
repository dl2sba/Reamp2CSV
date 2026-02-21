# *********************************************************************************
# ***                                                                           ***
# ***  Reamp exporter                                                           ***
# ***                                                                           ***
# ***  (c) DL2SBA Dietmar Krause 2026                                           ***
# ***                                                                           ***
# *********************************************************************************
import argparse
import struct
import csv
import locale
import sys
import os
import logging
from datetime import datetime
from datetime import timezone
from pathlib import Path

PARM_TIME_RELATIVE = "relative"
PARM_TIME_TIMESTAMP = "timestamp"
PARM_TIME_MICROS = "unix"


# *********************************************************************************
# ***                                                                           ***
# ***  Exporter                                                                 ***
# ***                                                                           ***
# *********************************************************************************
def process_reamp_data(
    parm_input_path,
    parm_output_path,
    parm_delimiter,
    parm_encoding,
    parm_time,
):
    num_channels = 0
    try:
        with open(parm_input_path, "rb") as in_file:
            #
            logging.info(f"inputfile size... {os.fstat(in_file.fileno()).st_size}")

            #   process header section
            binary_content = in_file.read(0x200)

            fileVersion = struct.unpack("<h", binary_content[0:2])[0]
            fileHeaderSize = struct.unpack("<h", binary_content[2:4])[0]
            fileChannelCount = struct.unpack("B", binary_content[8:9])[0]
            fileChannelMap = struct.unpack("B", binary_content[9:10])[0]
            fileSampleTime = (
                struct.unpack("<h", binary_content[10:12])[0] / 10
            )  # in ms ticks
            fileType = struct.unpack("B", binary_content[8:9])[0]
            fileStartTS = struct.unpack("<Q", binary_content[0x1F8:0x200])[0] / 1000

            logging.info(f"fileVersion...... {fileVersion}")
            logging.info(f"fileHeaderSize... {fileHeaderSize}")
            logging.info(f"fileChannelCount. {fileChannelCount}")
            logging.info(f"fileChannelMap... {fileChannelMap}")
            logging.info(f"fileSampleTime... {fileSampleTime}ms")
            logging.info(f"fileType......... {fileType}")
            logging.info(f"fileStartTS...... {fileStartTS}s")
            logging.info(
                f"                  {datetime.fromtimestamp(fileStartTS, tz=timezone.utc)}"
            )

            #   process data records
            with open(
                parm_output_path, "w", newline="", encoding=parm_encoding
            ) as outFile:
                writer = csv.writer(outFile, delimiter=parm_delimiter)
                writer.writerow(["time", "channel 0", "channel 1", "channel 2"])

                #   detector for end of file
                #   increments are in ms
                lastIncrement = -1
                increment = 0
                bytesPerChannel = (fileChannelCount + 1) * 8
                timestampFromIncrement = ""
                numSamples = 0
                #
                #   read the data lines
                while True:
                    valueArray = []
                    #   read all data of a sample
                    sampleRaw = in_file.read(bytesPerChannel)
                    #   read 8 byte double value
                    doubleIncrement = struct.unpack("<d", sampleRaw[0:8])[0]
                    #   convert to ms
                    increment = doubleIncrement
                    # print(increment)
                    if increment == lastIncrement:
                        break
                    else:
                        lastIncrement = increment

                    timestampFromIncrement = fileStartTS + increment

                    if parm_time == PARM_TIME_RELATIVE:
                        valueArray.append(locale.format_string("%f", increment))
                    elif parm_time == PARM_TIME_TIMESTAMP:
                        #   timestamp of current sample in ms
                        valueArray.append(
                            datetime.fromtimestamp(
                                timestampFromIncrement, tz=timezone.utc
                            )
                        )
                    else:
                        #   timestamp of current sample in s
                        valueArray.append(timestampFromIncrement)

                    for chanNo in range(fileChannelCount):
                        startIdx = chanNo * 8 + 8
                        stopIdx = startIdx + 8
                        chanVal = struct.unpack("<d", sampleRaw[startIdx:stopIdx])[0]
                        chanValLocale = locale.format_string("%f", chanVal)
                        valueArray.append(chanValLocale)
                    writer.writerow(valueArray)
                    if numSamples % 10000 == 0:
                        logging.info(f"samples written.. {numSamples}")
                    numSamples += 1

                logging.info(f"samples written.. {numSamples}")
                logging.info(f"fileLastTS....... {timestampFromIncrement}")
                logging.info(f"outputfile size.. {os.fstat(outFile.fileno()).st_size}")
                logging.info(f"                  {datetime.fromtimestamp(
                        timestampFromIncrement, tz=timezone.utc )}")
            logging.info("... bye ...")

    except FileNotFoundError as e:
        logging.error(f"Error: File '{e.filename}' not found")


# *********************************************************************************
# ***                                                                           ***
# ***  Main                                                                     ***
# ***                                                                           ***
# *********************************************************************************
def main():
    logging.basicConfig(
        level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # init Parser
    parser = argparse.ArgumentParser(
        description="Converts Reamp-Datafile into CSV-Format."
    )

    # mandatory parameter input filename
    parser.add_argument("input_file", help="filename of *.reamp datafile")

    # optional output file name
    parser.add_argument(
        "-o", "--output", help="Name of the output file (default: <inputfile>.csv)"
    )

    # optional locale
    parser.add_argument(
        "-l",
        "--locale",
        default="German",
        help="Locale used for number formatting (default: 'German')",
    )

    # optional output encoding
    parser.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="Encoding of output file (default: 'utf-8'). For details check https://docs.python.org/3/library/codecs.html",
    )

    # optional verbose
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose log output"
    )

    # optional delimeter
    parser.add_argument(
        "-d",
        "--delimiter",
        choices=[",", ";"],
        default=";",
        help="Value delimiter in CSV-file (default: ';')",
    )

    # optional mode of time column
    parser.add_argument(
        "-t",
        "--time",
        choices=[PARM_TIME_MICROS, PARM_TIME_RELATIVE, PARM_TIME_TIMESTAMP],
        default=PARM_TIME_RELATIVE,
        help=f"Time column in CSV (default: {PARM_TIME_RELATIVE})",
    )

    # parse args
    args = parser.parse_args()

    input_file_name = Path(args.input_file)
    output_file_name = (
        args.output if args.output else input_file_name.with_suffix(".csv")
    )
    locale_used = args.locale
    delimiter_used = args.delimiter
    encoding_used = args.encoding
    time_used = args.time

    if args.verbose:
        # CRITICAL	50
        # ERROR	40
        # WARNING	30
        # INFO	20
        # DEBUG	10
        logging.getLogger().setLevel(20)

    logging.info(f"*******************************************************************")
    logging.info(f"***                                                             ***")
    logging.info(f"***  Reamp exporter                                             ***")
    logging.info(f"***                                                             ***")
    logging.info(f"***    Repository  https://github.com/dl2sba/Reamp2CSV          ***")
    logging.info(f"***    Homepage    https://dl2sba.com                           ***")
    logging.info(f"***                                                             ***")
    logging.info(f"***  (c) DL2SBA Dietmar Krause 2026                             ***")
    logging.info(f"***                                                             ***")
    logging.info(f"*******************************************************************")
    logging.info(f"input filename... {input_file_name}")
    logging.info(f"output filename.. {output_file_name}")
    logging.info(f"locale used...... {locale_used}")
    logging.info(f"data delimiter... {delimiter_used}")
    logging.info(f"output encoding.. {encoding_used}")
    logging.info(f"time columns .... {time_used}")

    try:
        locale.setlocale(locale.LC_ALL, locale_used)

        process_reamp_data(
            input_file_name, output_file_name, delimiter_used, encoding_used, time_used
        )

    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


# *********************************************************************************
# ***                                                                           ***
# ***  Launcher                                                                 ***
# ***                                                                           ***
# *********************************************************************************
if __name__ == "__main__":
    main()
