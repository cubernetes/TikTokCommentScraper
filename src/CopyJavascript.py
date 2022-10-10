#!/usr/bin/env python3

from pyperclip import copy, PyperclipException
import os

os.system("")
try:
    copy(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),  "ScrapeTikTokComments.js"), encoding="utf-8").read())
    print("\x1b[32mCopied to clipboard!\x1b[0m") 
except PyperclipException:
    print("Could not find copy/paste mechanism on this system. Please copy the javascript manually from https://raw.githubusercontent.com/cubernetes/TikTokCommentScraper/main/src/ScrapeTikTokComments.js")
