# Website-Scanner
Website Scanner can scan a website for broken links and search for specific strings and/or files with the help of multiple concurrently running web crawlers. 
## Features:
  *	GUI based.
  *	AutoSaves progress every 2 minutes.
  *	Extracts and saves domain registration information of the site.
  *	Left Click any URL shown in output to open it and Right Click to copy it.
  *	Activity Logging
  *	Automatically download searched file.
  *	Downloading can be resumed if supported by the site.
  *	Multiple instances support.
  *	Shows warning when an instance tries to start a project which is already run by another instance.
  *	Shows Current Session and All Sessions statistics.
  *	Four output panes in can be resized by user.
  *	Waits for all crawlers to stop before exit.

## Software Requirements 
  *	Python 3 - External libraries required:
    *	Requests - Requests allows you to send HTTP/1.1 requests.
    *	bs4 - Beautiful Soup sits atop an HTML or XML parser, providing Pythonic idioms for iterating, searching, and modifying the parse tree.
    *	validators - Python Data Validation for Humans™.
    *	robotexclusionrulesparser - A robots.txt parser for python.
    *	tld - Extract the top level domain (TLD) from the URL given.
    *	python-whois - Whois querying and parsing of domain registration information.
## Hardware Requirements 
  *	Must be connected to internet.
  *	Must have enough space to store the data files and requested files. (Space required depends on the website which is to be scanned and options selected by user.)
## How to run
* Ensure all the mentioned requirements are fulfilled.
* Execute run.bat file.



