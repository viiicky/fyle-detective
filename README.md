# fyle-detective

Quick utility to help you debug your bugs like never before. This utility is the sister-utility of the chrome extension [fyle-inspector](https://github.com/viiicky/fyle-inspector)

## Usage:
`python fyle_detective.py <evidence_url>`


## Description
`fyle-inspector` inspects all the evidence from a page and post it to a url. Let's call it `evidence_url`.
`fyle-detective` analyses the evidence from this `evidence_url` and does the following three things:
1. It saves the screeshot of the crime-scene(read web-page when it broke) on your machine by the name `screenshot.png`.
2. It saves the detailed crime-report on your machine by the name `evidence.json`. This file contains all sort of information, like:
	- url: the web-url on which the app broke
	- local_storage: the complete local storage from the client during the time of crime
	- system_info: browser details, machine details etc.
	- log_data: all the messages that were logged on console
3. It creates a Freshdesk ticket attaching the above screenshot and evidence and putting out highlights of the report as description of the ticket.

### Preview
![Freshdesk Screenshot](/fd.png)

Note: Make sure you install the relevant dependencies and have the relevant environment variables set in your system for this script to function.
