#!/usr/bin/python

'''
python test5.py --title "title" --tag "lecture,R" --content "content"
'''

filename = "na.db"
authorId = 1

import argparse
import datetime
parser = argparse.ArgumentParser()
parser.add_argument("--title", type=str, help="title (short)")
parser.add_argument("--tag", type=str, help="comma-separated tags")
parser.add_argument("--content", type=str, help="content (long; markdown format)")
args = parser.parse_args()
if args.tag:
    tags = args.tag.split(',')
else:
    print "must give args"
    exit
if args.title:
    title = args.title
else:
    title = ""
if args.content:
    content = args.content
else:
    content = ""

import sqlite3 as sqlite
import sys

con = sqlite.connect(filename)
if not con:
    print "error opening connection"
    exit(1)
cur = con.cursor()
data_union = ()
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d %H:%M:%S")
print "date '%s'" % date
cmd = "INSERT INTO note(authorId, date, title, content, views) VALUES(%d, '%s', '%s', '%s', %d)" % (authorId, date, title, content, 0)
print cmd
cur.execute(cmd)
noteId = cur.lastrowid
print "noteid %s" % noteId
for tag in tags:
    print "tag '%s'" % tag
    cmd = "select tagId from tag WHERE tag='%s';" % tag
    print cmd
    cur.execute(cmd)
    tagId = cur.fetchone()[0]
    # FIXME: if not found, create a new tag
    cmd = "INSERT INTO notetag(noteId, tagID) VALUES(%d, %d)" % (noteId, tagId)
    print cmd
    cur.execute(cmd)

con.commit()
con.close()

