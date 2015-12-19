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
import ipaddress
import re
import sys

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def remove_signatures(user, message):
    """Tries to remove the user signature from the messages. Not always possible because of the customized signatures"""
    signature = "[—-]{0,2}(&nbsp;| )?(<(span|div) .*>)?\[\[(Discussion utilisat(eur|rice)|Utilisat(eur|rice)|User):"
    signature += user
    signature +=".* à \d{1,2}:\d{1,2} \(CES?T\)"
    message = re.sub(signature, ' ', message)
    return message

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

            if authorized_user(user):
                if 'diff' in rev.keys():
                    if '*' in rev['diff']:
                        soup = BeautifulSoup(rev['diff']['*'])
                        newlines = soup.select('.diff-addedline')
                        for n in newlines:
                            
                            text = n.text.lstrip(':').strip()

                            if not titles.match(text):
                                text = remove_signatures(user, text)

                                # remove most html tags
                                text = re.sub('<[^<]+?>', '', text)

                                if "{{non signé|" in text:
                                    text =""

                                if text == '@':
                                    text = ''

                                if user not in users_sentences.keys():
                                    users_sentences[user] = []
                                if len(text) and text not in users_sentences[user]:
                                    users_sentences[user].append(text)
                                
                            else:
                                section_titles.append(text)

    if "continue" in data.keys():
        print("continue tag: " + data['continue']['rvcontinue'])
        parse_result(url, data['continue']['rvcontinue'])

def save_text(user, text):
    if len(text):
        user_file = users_dir + user.replace(' ', '_') + '.txt'
        with open(user_file,"a") as f:
            f.write(text + '\n')
            f.close()

def authorized_user(user):
    """Check if we want to register this user's edits or not."""
    auth = False

    # Exclude bots
    ban_list = ['NaggoBot', 'ZéroBot', 'HerculeBot']

    # Exclude anonymous
    if user not in ban_list:
        try: 
            ipaddress.ip_address(user)
        except ValueError:
            auth = True

    return auth

# Get the contents
if len(sys.argv) > 1:
    date_fragments = sys.argv[1].split('-')
    base = datetime.datetime(int(date_fragments[0]),int(date_fragments[1]),int(date_fragments[2]))
else:
    base = datetime.datetime.today()

if len(sys.argv) > 2:
    backlog = int(sys.argv[2])
else:
    backlog = 30 # the number of days of "Bistro" page to parse from today

# variables
users_dir = 'users/'
titles = re.compile('={1,6} ?.* ?={1,6}')


root_url = "https://fr.wikipedia.org"
api_url = root_url + "/w/api.php?"
dates_list = [format_date(base - datetime.timedelta(days=x), locale='fr_FR', format='long') for x in range(0, backlog)]

for date in dates_list:
    users_sentences = {}
    section_titles = []

    print("{} ".format(date))
    params = {
        "action" : "query",
        "prop" : "revisions",
        "format" : "json",
        "rvprop" : "user",
        "rvlimit" : 1,
        "rvdiffto" : "prev",
        "titles" : "Wikipédia:Le Bistro/{}".format(date) }
    
    api_call =  api_url + urllib.parse.urlencode(params)
    # Parameter rvlimit set to 1 because of bug https://phabricator.wikimedia.org/T31223

    parse_result(api_call)

    for user, chunks in users_sentences.items():
        text = "\n".join(chunks)
        save_text(user, text)

    save_text('section_titles', '\n'.join(section_titles))