# Reamp to CSV Converter
A Python utility for converting recording data from the `*.reamp` format into standardized CSV files.

## Features
- Supports various localizations for number formatting.
- High-precision timestamps down to the microsecond range (µs).
- Automated scaling of units (voltage in mV, current in µA).

## Installation
Ensure that Python is installed on your system. Clone the repository and navigate to the folder.

## Usage
The script is called via the command line with one required parameter. For a detailled description call the script with the `-h` parameter

```
usage: Reamp2CSV.py [-h] [-d {,,;}] [-e ENCODING] [-l LOCALE] [-o OUTPUT] [-t {unix,relative,timestamp}] [-v] input_file

Converts Reamp-Datafile into CSV-Format.

positional arguments:
  input_file            filename of *.reamp datafile

options:
  -h, --help            show this help message and exit
  -d, --delimiter {,,;}
                        Value delimiter in CSV-file (default: ;)
  -e, --encoding ENCODING
                        Encoding of output file. For details check
                        https://docs.python.org/3/library/codecs.html (default: utf-8)
  -l, --locale LOCALE   Locale used for number formatting (default: EN_US)
  -o, --output OUTPUT   Name of the output file (default: <inputfile>.csv) (default: None)
  -t, --time {unix,relative,timestamp}
                        Time column in CSV (default: relative)
  -v, --verbose         Verbose log output (default: False)
```

## CSV-Struktur (Output)
The generated CSV file uses a semicolon ; as a separator and contains the following columns:

| Column | Description |
| :--- | :--- |
| `1` | Time formatted according to parameter `--time` |
| `2` | Channel 1: Measurement data (voltage in mV / current in µA) |
| `3` | Channel 2: Optional Second channel (voltage in mV / current in µA)|
| `4` | Channel 3: Optional Third channel (voltage in mV / current in µA)|

## EXCEL-Import
Excel currently only supports a time resolution down to the millisecond range (ms) natively. To display the timestamps correctly:
- Open the CSV file in Excel.
- Select the column with the timestamp.
- Select Format Cells -> Custom.
- Use the following format:
  - For Enlish version `DD.MM.YYYY hh:mm:ss,000`
  - For German version `TT.MM.JJJJ hh:mm:ss,000`

## Support
You can send comments and bug reports directly vie the issue tracking in github
