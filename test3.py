#!/usr/bin/python

'''
Try e.g.

python test3.py --note "contents of the test note" --tag "tag1,tag2" --title 'test note'

'''

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--note", type=str, help="contents of the note")
parser.add_argument("--title", type=str, help="title of the note")
parser.add_argument("--tag", type=str, help="comma-separated tags")
args = parser.parse_args()
if args.note:
    print "should create a note with content '%s'" % args.note
if args.title:
    print "  title '%s'" % args.title
if args.tag:
    tags = args.tag.split(',')
    for tag in tags:
        print "  tagged '%s'" % tag

