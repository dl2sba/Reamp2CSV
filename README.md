# Reamp to CSV Converter

Ein Python-Utility zum Konvertieren von Aufzeichnungsdaten aus dem `*.reamp`-Format in standardisierte CSV-Dateien.

## Features

- Unterstützt verschiedene Lokalisierungen für die Zahlenformatierung.
- Hochpräzise Zeitstempel bis in den Mikrosekundenbereich (µs).
- Automatisierte Skalierung von Einheiten (Spannung in mV, Strom in µA).

## Installation

Stelle sicher, dass Python auf deinem System installiert ist. Klone das Repository und navigiere in den Ordner:

```bash
git clone https://github.com
cd DEIN-REPRO-NAME
Verwende Code mit Vorsicht.

Verwendung
Das Skript wird über die Kommandozeile mit drei erforderlichen Parametern aufgerufen:
bash
python scriptName.py <locale> <input_file> <output_file>
Verwende Code mit Vorsicht.

Parameter
Parameter	Beschreibung
locale	'German' für Komma , oder 'US' für Punkt . als Dezimaltrenner.
input_file	Pfad zur Quelldatei im *.reamp Format.
output_file	Zielpfad für die CSV-Datei.
CSV-Struktur (Output)
Die erzeugte CSV-Datei verwendet ein Semikolon ; als Trennzeichen und enthält folgende Spalten:
Relative Zeit: In µs seit Beginn der Aufzeichnung.
Absolute Zeit: UTC-Zeitstempel (vollqualifiziert bis µs).
Kanal 1: Messdaten (Spannung in mV / Strom in µA).
Kanal 2: (Optional) Zweiter Kanal.
Kanal 3: (Optional) Dritter Kanal.
Einschränkung: Die ChannelMap wird derzeit nicht unterstützt.
Import in Excel
Excel unterstützt nativ derzeit nur eine Zeitauflösung bis in den Millisekundenbereich (ms). Um die Zeitstempel korrekt anzuzeigen:
Öffne die CSV in Excel.
Markiere die Spalte mit dem Zeitstempel.
Wähle Zellen formatieren -> Benutzerdefiniert.
Nutze folgendes Format: TT.MM.JJJJ hh:mm:ss,000
Support
Kommentare und Fehlerberichte kannst du direkt an labview@dl2sba.de senden.
