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
    with open(parm_input_path, "rb") as in_file:
        #
        logging.info("inputfile size.....%ld", os.fstat(in_file.fileno()).st_size)

        #   process header section
        binary_content = in_file.read(0x200)

        #   extract header fields
        file_version = struct.unpack("<h", binary_content[0:2])[0]
        file_header_size = struct.unpack("<h", binary_content[2:4])[0]
        file_channel_count = struct.unpack("B", binary_content[8:9])[0]
        file_channel_map = struct.unpack("B", binary_content[9:10])[0]
        file_sample_time = (
            struct.unpack("<h", binary_content[10:12])[0] / 10
        )  # in ms ticks
        file_type = struct.unpack("B", binary_content[8:9])[0]
        file_start_ts = struct.unpack("<Q", binary_content[0x1F8:0x200])[0] / 1000

        logging.info("file_version.......%s", file_version)
        logging.info("file_header_size...%s", file_header_size)
        logging.info("file_channel_count.%d", file_channel_count)
        logging.info("file_channel_map...%s", file_channel_map)
        logging.info("file_sample_time...%s ms", file_sample_time)
        logging.info("file_type......... %d", file_type)
        logging.info("file_start_ts......%s s", file_start_ts)
        logging.info("                   %s", datetime.fromtimestamp(file_start_ts, tz=timezone.utc))

        #   check file version
        if file_version != 4:
            raise ValueError("Fileversion not supported")

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
                value_array = []
                #   read all data of a sample
                sample_raw = in_file.read(bytes_per_channel)
                #   read 8 byte double value
                double_increment = struct.unpack("<d", sample_raw[0:8])[0]
                #   convert to ms
                increment = double_increment
                # print(increment)
                if increment == last_increment:
                    break

                last_increment = increment
                timestamp_from_increment = file_start_ts + increment

                if parm_time == PARM_TIME_RELATIVE:
                    value_array.append(locale.format_string("%f", increment))
                elif parm_time == PARM_TIME_TIMESTAMP:
                    #   timestamp of current sample in ms
                    value_array.append(
                        datetime.fromtimestamp(
                            timestamp_from_increment, tz=timezone.utc
                        )
                    )
                else:
                    #   timestamp of current sample in s
                    value_array.append(timestamp_from_increment)

                # process each channel in a row
                for chan_no in range(file_channel_count):
                    start_idx = chan_no * 8 + 8
                    stop_idx = start_idx + 8
                    chan_value = struct.unpack("<d", sample_raw[start_idx:stop_idx])[0]
                    chan_value_locale = locale.format_string("%f", chan_value)
                    value_array.append(chan_value_locale)

                writer.writerow(value_array)

                # cyclic status update
                if num_samples % 10000 == 0:
                    logging.info("samples written..%d", num_samples)
                num_samples += 1

            logging.info("samples written....%d", num_samples)
            logging.info("fileLastTS.........%s", timestamp_from_increment)
            logging.info("outputfile size....%d", os.fstat(out_file.fileno()).st_size)
            logging.info("                   %s", datetime.fromtimestamp(timestamp_from_increment, tz=timezone.utc ))
        logging.info("... bye ...")


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

    logging.info("*******************************************************************")
    logging.info("***                                                             ***")
    logging.info("***  Reamp exporter                                             ***")
    logging.info("***                                                             ***")
    logging.info("***    Repository  https://github.com/dl2sba/Reamp2CSV          ***")
    logging.info("***    Homepage    https://dl2sba.com                           ***")
    logging.info("***                                                             ***")
    logging.info("***  (c) DL2SBA Dietmar Krause 2026                             ***")
    logging.info("***                                                             ***")
    logging.info("*******************************************************************")
    logging.info("input filename.....%s", input_file_name)
    logging.info("output filename....%s", output_file_name)
    logging.info("locale used........%s", locale_used)
    logging.info("data delimiter.....%s", delimiter_used)
    logging.info("output encoding....%s", encoding_used)
    logging.info("time column........%s", time_used)

    # pylint: disable=broad-exception-caught
    try:
        locale.setlocale(locale.LC_ALL, locale_used)

        process_reamp_data(
            input_file_name, output_file_name, delimiter_used, encoding_used, time_used
        )

    except Exception as e:
        logging.error("Ein unerwarteter Fehler ist aufgetreten: [%s]", e)

# *********************************************************************************
# ***                                                                           ***
# ***  Launcher                                                                 ***
# ***                                                                           ***
# *********************************************************************************
if __name__ == "__main__":
    main()
