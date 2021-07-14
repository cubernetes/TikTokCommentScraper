# What can this comment scraper do?
This comment scraper/extractor/crawler manages to get all the comments
from any TikTok post. This can be usefull for giveaways, votes or other bigger
community interactions.

# How does it work?/How to use it?
This comment scraper uses the chrome developer console (chromium based browser
recommended/maybe needed), JavaScript and Python. The JavaScript (which is
documentated and located in '.\python38\Scrape TikTok Comments.js' from the
project's root directory) is copied to the clipboard when the '.\Extract
Comments from Clipboard.cmd' file is run. With the TikTok post open (so you can
see and scroll the comments), open the developer console with F12,
CTRL+SHIFT+I, CTRL+SHIFT+C or somehow through the settings. In the interactive
console tab, paste the JavaScript and execute it. To be sure the JavaScript
hasn't been tampered, you should maybe look through it once more before you run
it to look out for anything malicious (you never know!). The original file
doesn't make any requests; the clipboard action is the only security critical
task.

After you ran the JavaScript, wait. Depending on the number of comments, it
should go reasonable fast. Anything below 200 comments should go quite quick,
anything below 3000 comments should be done in under 1-2 minutes and the
performance usually shouldn't suffer. While you wait, the JavaScript scrolls to
the last loaded comments which forces TikTok to load new comments. This process
is repeated until no new comments load for 30 iterations. Then the 2nd level
comments get loaded (all the replies). The JavaScript clicks all the 'Read
More' buttons until no more new comments appear for 5 iterations. After those 2
processes, all comments should be rendered. In the 3rd phase, the JavaScript
reads all the comments and organizes them and converts them to the CSV format.
In the end, one big string that is the CSV-format will be copied to the
clipboard.

When the debug message 'CSV copied to clipboard!' appears, it's finished. Now,
without copying anything new obviously, run the '.\Copy JavaScript for
Developer Console.cmd' file. It will fetch the csv formatted clipboard content
and convert it to a .xlsx file which can be opened in LibreOffice Calc or
Microsoft Excel.

# Limits
This comment scraper was tested on a few posts with up to 3000 commments on a
middle- tier lenovo laptop where it got a little bit laggy during the comment
loading phase. A PC with much RAM is recommended which then should be able to
scrape 10k+ comments without major performance problem.

Another caveat is TikTok's limitations for showing all comments. Even with only
a few hundred comments, TikTok fails to show the 'correct' number of comments.
E.g. it says in the icon that there are 750 but when you load/render literally
all comments, you only count 740, which happens pretty much always with many
comments. In the 3000 comments test, 64 comments were never loaded and
therefore not included in the .xlsx file. Fortunately, this percentage is
negligible.
