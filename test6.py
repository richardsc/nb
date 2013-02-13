#!/usr/bin/python

'''
python test6.py --title "oceanpython lecture" --tag "lecture,python" --content "Diego gave a great talk"
'''
debug = 1

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
cmd = "INSERT INTO note(authorId, date, title, content, views) VALUES(%d, '%s', '%s', '%s', %d)" % (authorId, date, title, content, 0)
if debug:
    print cmd
cur.execute(cmd)
noteId = cur.lastrowid
for tag in tags:
    cmd = "SELECt tagId FROM tag WHERE tag='%s';" % tag
    if debug:
        print cmd
    cur.execute(cmd)
    tagId = cur.fetchone()
    if tagId:
        tagId = tagId[0]
    else:
        cmd = "INSERT INTO tag(tag) VALUES ('%s');" % tag
        if debug:
            print cmd
        cur.execute(cmd)
        tagId = cur.lastrowid
        # FIXME: should check whether the insertion worked
    cmd = "INSERT INTO notetag(noteId, tagID) VALUES(%d, %d)" % (noteId, tagId)
    if debug:
        print cmd
    cur.execute(cmd)

con.commit()
con.close()

