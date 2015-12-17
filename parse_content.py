#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script parses the diffs of a Wikipedia page to get all edit contents and store them in plain text files, user per user.
"""

import urllib
import json
from bs4 import BeautifulSoup
import datetime
from babel.dates import format_date, format_datetime, format_time

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def parse_result(url, next_batch = ""):
    if next_batch:
        response = urlopen(url + '&rvcontinue=' + next_batch)
    else:
        response = urlopen(url)

    data = json.loads(response.read().decode('utf-8'))
    pages = data['query']['pages']

    for p in pages.keys():
        revisions = pages[p]['revisions']
        
        for rev in revisions:
            if 'user' in rev.keys():
                user = rev['user']
            else:
                user = "unknown"
            if 'diff' in rev.keys():
                if '*' in rev['diff']:
                    soup = BeautifulSoup(rev['diff']['*'])
                    newlines = soup.select('.diff-addedline')
                    for n in newlines:
                        text = n.text.lstrip(':').strip()
                        save_text(user, text)

    if "continue" in data.keys():
        print("continue tag: " + data['continue']['rvcontinue'])
        parse_result(url, data['continue']['rvcontinue'])

def save_text(user, text):
    user_file = users_dir + user.replace(' ', '_') + '.txt'
    with open(user_file,"a") as f:
        f.write(text + ' ')
        f.close()

# Get the contents
users_dir = 'users/'

root_url = "https://fr.wikipedia.org"

base = datetime.datetime.today()
dates_list = [format_date(base - datetime.timedelta(days=x), locale='fr_FR', format='long') for x in range(0, 365)]

for date in dates_list:
    print("{} ".format(date))
    page_titles = { "titles" : "Wikipédia:Le Bistro/{}".format(date) }
    
    api_call =  root_url + "/w/api.php?action=query&prop=revisions&format=json&rvprop=user&rvlimit=500&rvdiffto=prev&" + urllib.parse.urlencode(page_titles)

    parse_result(api_call)