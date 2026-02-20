# Reamp to CSV Converter
A Python utility for converting recording data from the `*.reamp` format into standardized CSV files.

## Features
- Supports various localizations for number formatting.
- High-precision timestamps down to the microsecond range (µs).
- Automated scaling of units (voltage in mV, current in µA).

## Installation
Ensure that Python is installed on your system. Clone the repository and navigate to the folder.

## Verwendung
The script is called via the command line with three required parameters:

   python scriptName.py <locale> <input_file> <output_file>

## Parameter
| Parameter | Beschreibung |
| :--- | :--- |
| `locale` | **'German'** für Komma `,` oder **'US'** für Punkt `.` als Dezimaltrenner. |
| `input_file` | Pfad zur Quelldatei im `*.reamp` Format. |
| `output_file` | Zielpfad für die CSV-Datei. |


## CSV-Struktur (Output)
Die erzeugte CSV-Datei verwendet ein Semikolon ; als Trennzeichen und enthält folgende Spalten:
| Spalte | Beschreibung |
| :--- | :--- |
| `1` | Relative Zeit: In µs seit Beginn der Aufzeichnung |
| `2` | Absolute Zeit: UTC-Zeitstempel (vollqualifiziert bis µs) |
| `3` | Kanal 1: Messdaten (Spannung in mV / Strom in µA) |
| `4` | Kanal 2: (Optional) Zweiter Kanal |
| `5` | Kanal 3: (Optional) Dritter Kanal |

## EXCEL-Import
Excel unterstützt nativ derzeit nur eine Zeitauflösung bis in den Millisekundenbereich (ms). Um die Zeitstempel korrekt anzuzeigen:
- Öffne die CSV in Excel.
- Markiere die Spalte mit dem Zeitstempel.
- Wähle Zellen formatieren -> Benutzerdefiniert.
- Nutze folgendes Format: TT.MM.JJJJ hh:mm:ss,000

## Support
Kommentare und Fehlerberichte kannst du direkt an `labview@dl2sba.de` senden.
