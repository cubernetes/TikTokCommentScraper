#!/usr/bin/env python3

import sys
from csv import reader
from os import system, getcwd, remove, path
from datetime import datetime as d
from pyperclip import paste, PyperclipException
from openpyxl import Workbook

cur_dir = path.dirname(path.abspath(__file__))
csv_path = path.join(cur_dir, "..", "Comments.csv")

# Needed to initialize the prompt to support ansi escape sequences
system("")

try:
	csv = paste()
except PyperclipException:
	print("\x1b[31m[*]\x1b[0m Could not find copy/paste mechanism on this system. Please paste the csv below and end the input with an empty line:")
	aux = ''
	csv = '\n'.join(iter(input, aux))
try:
	print("\x1b[34m[*]\x1b[0m Writing CSV from clipboard to file +" \
		" removing carriage return characters ('\\r').", end="", flush=True)
	open(csv_path, "w", encoding="utf-8").write(csv.replace("\r","\n").replace("\n\n","\n"))
except Exception as e:
	print(e)
	print("\n\x1b[31m[X]\x1b[0m Couldn't write to CSV file. Does it already exist?")
	sys.exit(1)


print("\r\x1b[32m[*]\x1b[0m Writing CSV from clipboard to file + removing carriage return characters ('\\r').")

wb = Workbook()
ws = wb.active

print("\x1b[34m[*]\x1b[0m Converting CSV file to Excel Workbook (XLSX).", end="", flush=True)
line_count = 0
with open(csv_path, 'r+', encoding="utf-8") as f:
	for row in reader(f):
		ws.append(row)
		line_count += 1

print("\r\x1b[32m[*]\x1b[0m Converting CSV file to Excel Workbook (XLSX).")

print(f"\x1b[32m[*]\x1b[0m Written {line_count} line(s).")

print("\x1b[34m[*]\x1b[0m Saving XLSX file.", end="", flush=True)

wb.save(path.join(cur_dir, "..", f"Comments_{d.timestamp(d.now())}.xlsx"))

print("\r\x1b[32m[*]\x1b[0m Saving XLSX file.")

print("\x1b[34m[*]\x1b[0m Deleting CSV file.", end="", flush=True)

print("\r\x1b[34m[*]\x1b[0m Deleting CSV file.", end="")
try:
	remove(path.join(cur_dir, "..", "Comments.csv"))
	print("\r\x1b[32m[*]\x1b[0m Deleting CSV file.")
except:
	print("\r\x1b[31m[*]\x1b[0m Could not delete CSV file.")


print("\x1b[32m[*]\x1b[0m Done.", end="\n\n")
