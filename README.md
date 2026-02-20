# Reamp to CSV Converter
A Python utility for converting recording data from the `*.reamp` format into standardized CSV files.

## Features
- Supports various localizations for number formatting.
- High-precision timestamps down to the microsecond range (µs).
- Automated scaling of units (voltage in mV, current in µA).

## Installation
Ensure that Python is installed on your system. Clone the repository and navigate to the folder.

## Usage
The script is called via the command line with three required parameters:

   python scriptName.py <locale> <input_file> <output_file>

## Parameter
| Parameter | Description |
| :--- | :--- |
| `locale` | **'German'** für commy `,` or **'US'** für dot `.` decimal seperator |
| `input_file` | source filename in `*.reamp` format |
| `output_file` | target filename in `*.reamp` format |


## CSV-Struktur (Output)
The generated CSV file uses a semicolon ; as a separator and contains the following columns:

| Column | Description |
| :--- | :--- |
| `1` | Relative time: In µs since the start of recording |
| `2` | Absolute time: UTC timestamp (fully qualified to µs) |
| `3` | Channel 1: Measurement data (voltage in mV / current in µA) |
| `4` | Channel 2: (Optional) Second channel |
| `5` | Channel 3: (Optional) Third channel |

## EXCEL-Import
Excel currently only supports a time resolution down to the millisecond range (ms) natively. To display the timestamps correctly:
- Open the CSV file in Excel.
- Select the column with the timestamp.
- Select Format Cells -> Custom.
- Use the following format: `DD.MM.YYYY hh:mm:ss,000`

## Support
You can send comments and bug reports directly to `labview@dl2sba.de`.
