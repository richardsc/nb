#!/usr/bin/python

'''
na --action add --title "oceanpython lecture" --keyword "lecture,python" --content "Diego gave a great talk"
na --action find --keyword "lecture"
'''

import sys
from naclass import na

import argparse
import datetime
import sys
parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, help="action ('add' or 'find')", choices=['add', 'find'])
parser.add_argument("--title", type=str, help="title (short)")
parser.add_argument("--keyword", type=str, help="comma-separated keywords")
parser.add_argument("--content", type=str, help="content (long; markdown format)")
parser.add_argument("--debug", action="store_true", dest="debug", default=False, help="set debugging on")
args = parser.parse_args()
debug = args.debug

if args.keyword:
    if args.action=="add":
        keywords = args.keyword.split(',')
    else:
        keywords = args.keyword.split(',') # FIXME: allow also |
if args.title:
    title = args.title
else:
    title = ""
if args.content:
    content = args.content
else:
    content = ""

na = na()
if args.action == "add":
    na.add(title, content)

if args.action == "find":
    na.find(keywords)

    
