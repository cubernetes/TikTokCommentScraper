#!/usr/bin/env python3

from pyperclip import copy
import os

os.system("")
copy(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),  "ScrapeTikTokComments.js"), encoding="utf-8").read())
print("\x1b[32mCopied to clipboard!\x1b[0m")
