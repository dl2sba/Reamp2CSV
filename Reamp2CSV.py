"""
*********************************************************************************
***                                                                           ***
***  Reamp exporter                                                           ***
***                                                                           ***
***  (c) DL2SBA Dietmar Krause 2026                                           ***
***                                                                           ***
*********************************************************************************
"""

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


def process_reamp_data(
    parm_input_path,
    parm_output_path,
    parm_delimiter,
    parm_encoding,
    parm_time,
):
    """
    *********************************************************************************
    ***                                                                           ***
    ***  Exporter                                                                 ***
    ***                                                                           ***
    *********************************************************************************
    """
    """
    *********************************************************************************
    ***                                                                           ***
    ***  Exporter                                                                 ***
    ***                                                                           ***
    *********************************************************************************
    """
    try:
        with open(parm_input_path, "rb") as in_file:
            #
            logging.info(f"inputfile size... {os.fstat(in_file.fileno()).st_size}")

            #   process header section
            binary_content = in_file.read(0x200)

            file_version = struct.unpack("<h", binary_content[0:2])[0]
            file_header_size = struct.unpack("<h", binary_content[2:4])[0]
            file_channel_count = struct.unpack("B", binary_content[8:9])[0]
            file_channel_map = struct.unpack("B", binary_content[9:10])[0]
            file_sample_time = (
                struct.unpack("<h", binary_content[10:12])[0] / 10
            )  # in ms ticks
            file_type = struct.unpack("B", binary_content[8:9])[0]
            file_start_ts = struct.unpack("<Q", binary_content[0x1F8:0x200])[0] / 1000

            logging.info(f"file_version...... {file_version}")
            logging.info(f"file_header_size... {file_header_size}")
            logging.info(f"file_channel_count. {file_channel_count}")
            logging.info(f"file_channel_map... {file_channel_map}")
            logging.info(f"file_sample_time... {file_sample_time}ms")
            logging.info(f"file_type......... {file_type}")
            logging.info(f"file_start_ts...... {file_start_ts}s")
            logging.info(
                f"                  {datetime.fromtimestamp(file_start_ts, tz=timezone.utc)}"
            )

            #   process data records
            with open(
                parm_output_path, "w", newline="", encoding=parm_encoding
            ) as out_file:
                writer = csv.writer(out_file, delimiter=parm_delimiter)
                writer.writerow(["time", "channel 0", "channel 1", "channel 2"])

                #   detector for end of file
                #   increments are in ms
                last_increment = -1
                increment = 0
                bytes_per_channel = (file_channel_count + 1) * 8
                timestamp_from_increment = ""
                num_samples = 0
                #
                #   read the data lines
                while True:
                    valueArray = []
                    #   read all data of a sample
                    sample_raw = in_file.read(bytes_per_channel)
                    #   read 8 byte double value
                    double_increment = struct.unpack("<d", sample_raw[0:8])[0]
                    #   convert to ms
                    increment = double_increment
                    # print(increment)
                    if increment == last_increment:
                        break
                    else:
                        last_increment = increment

                    timestamp_from_increment = file_start_ts + increment

                    if parm_time == PARM_TIME_RELATIVE:
                        valueArray.append(locale.format_string("%f", increment))
                    elif parm_time == PARM_TIME_TIMESTAMP:
                        #   timestamp of current sample in ms
                        valueArray.append(
                            datetime.fromtimestamp(
                                timestamp_from_increment, tz=timezone.utc
                            )
                        )
                    else:
                        #   timestamp of current sample in s
                        valueArray.append(timestamp_from_increment)

                    for chanNo in range(file_channel_count):
                        start_idx = chanNo * 8 + 8
                        stop_idx = start_idx + 8
                        chan_value = struct.unpack("<d", sample_raw[start_idx:stop_idx])[0]
                        chan_value_locale = locale.format_string("%f", chan_value)
                        valueArray.append(chan_value_locale)
                    writer.writerow(valueArray)
                    if num_samples % 10000 == 0:
                        logging.info(f"samples written.. {num_samples}")
                    num_samples += 1

                logging.info(f"samples written.. {num_samples}")
                logging.info(f"fileLastTS....... {timestamp_from_increment}")
                logging.info(f"outputfile size.. {os.fstat(out_file.fileno()).st_size}")
                logging.info(f"                  {datetime.fromtimestamp(timestamp_from_increment, tz=timezone.utc )}")
            logging.info("... bye ...")

    except FileNotFoundError as e:
        logging.error(f"Error: File '{e.filename}' not found")


def main():
    """
    *********************************************************************************
    ***                                                                           ***
    ***  Main                                                                     ***
    ***                                                                           ***
    *********************************************************************************
    """
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
