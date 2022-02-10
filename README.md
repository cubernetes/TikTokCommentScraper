# Functionality
This comment scraper/extractor manages to get all the comments
from virtually any TikTok post. This can be useful for giveaways, votes or other bigger
community interactions.

# Installation
Contrary to convention, this repo does contain the virtual environment it's
running on (**Windows**, for Linux see below), so it's instantly usable also for people how don't want to first install python and requirements.
The python environment is heavily stripped down (\~7MB).
Installation is as easy as:

`git clone https://github.com/cubernetes/TikTokCommentScraper`

Alternatively, download the zip directly if you don't have git installed:

`curl -L -o "TikTokCmtScraper.zip" https://github.com/cubernetes/TikTokCommentScraper/archive/refs/heads/main.zip`

If you're running Windows 7 and therefore don't even have curl installed, just download the zip directly from this repo and extract it.

# Requirements
Python requirements would be (if you don't want to use the venv or if you aren't using Windows):

`pyperclip`

`openpyxl`

# Usage
## TL;DR
- open your favorite **chromium** (e. g. Chrome, Brave, Chromium) based browser
- go to the TikTok post you want to scrape the comments from (make sure you can already scroll the comments manually)
- press F12 (goto developer console) or CTRL+SHIFT+J (should open the console directly)
- open Windows file explorer in root of this project folder (where the .cmd files are)
- double click 'Copy JavaScript for Developer Console.cmd'
	- **if you're not using Windows**, just run the src/CopyJavascript.py file manually with python (see requirements)
- go back to developer console; paste the javascript; run it
- wait until it says 'CSV copied to clipboard!'
- go back to file explorer; double click 'Extract Comments from Clipboard.cmd'
	- **if you're not using Windows**, just run the src/ScrapeTikTokComments.py file manually with python (see requirements)
- voilá, the file 'Comments_<UtcTimeStamp>.xlsx' will now contain all the comments and additional information

You can also watch this video: https://youtu.be/FsQEm2zalWA
or if you don't have time: https://youtu.be/lYZw75k7QVc

## In Detail

This comment scraper uses the chrome developer console (chromium based browser
recommended/maybe needed), JavaScript and Python. The JavaScript (which is
documentated and located in 'src\ScrapeTikTokComments.js') is copied to the clipboard when the '.\Copy
JavaScript for Developer Console.cmd' file is run (you can also copy
manually or run src/CopyJavascript.py). With the TikTok post open (so you can see and scroll the
comments), open the developer console with F12, CTRL+SHIFT+I/J, CTRL+SHIFT+C
or somehow through the settings. In the interactive console tab, paste the
JavaScript and execute it. To be sure the JavaScript hasn't been tampered,
you should maybe look through it once more before you run it to look out for
anything malicious. The original file doesn't make any requests; the clipboard action
is the only security critical task. NEVER mindlessly paste anything into the developer console (copying
foreign code to the console is considered a big security risk)! 

After you've ran the JavaScript, wait. Depending on the number of comments, it
should go reasonable fast. Anything below 200 comments should go quite quick,
anything below 3000 comments should be done in under 5 minutes and the
performance usually shouldn't suffer. While you wait, the JavaScript scrolls
to the last loaded comments which forces TikTok to load new comments. This
process is repeated until no new comments load for a few iterations. Then the
2nd level comments get loaded (all the replies). The JavaScript clicks all the
'Read More' buttons until no more new comments appear for 5 iterations. After those
2 processes, all comments should be rendered. In the 3rd phase, the JavaScript reads
all the comments and organizes them and converts them to CSV format. In the end, one big
string that is in CSV-format will be copied to the clipboard.

When the debug message 'CSV copied to clipboard!' appears, it's finished. Now,
without copying anything new obviously, click the 'Extract Comments from
Clipboard.cmd' file or run the src/ScrapeTikTokComments.py file manually (see requirements).
It will fetch the CSV-formatted clipboard content and
convert it to a .xlsx file which can be opened in e.g. LibreOffice Calc or
Microsoft Excel.

# Limits

This comment scraper was tested on a few posts with up to 3000 commments on a
middle-tier laptop where it got a little bit laggy during the comment loading
phase.

Another caveat is TikTok's limitations for showing all comments. Even with
only a few hundred comments, TikTok fails to show the 'correct' number of
comments. E.g. it says in the icon that there are 750 comments but when you
load/render all comments, you only count e.g. 740 comments, which happens
pretty much always with many comments. In the 3000 comments test, 64 comments
were never loaded and therefore not included in the .xlsx file. Fortunately,
this percentage is negligible most of the time.
