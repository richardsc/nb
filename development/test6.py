#!/usr/bin/python

'''
python test6.py --action add --title "oceanpython lecture" --keyword "lecture,python" --content "Diego gave a great talk"
python test6.py --action find --keyword "lecture"
python test6.py --action find --keyword "lecture+R"
'''

filename = "na.db"
authorId = 1

import argparse
import datetime
import sys
parser = argparse.ArgumentParser()
#parser.add_argument("string", metavar="action", type=str, help="add a note")
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

import sqlite3 as sqlite
import sys

con = sqlite.connect(filename)
if not con:
    print "error opening connection"
    exit(1)
cur = con.cursor()
data_union = ()

if args.action == "add":
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    cmd = "INSERT INTO note(authorId, date, title, content, views) VALUES(%d, '%s', '%s', '%s', %d)" % (authorId, date, title, content, 0)
    if debug:
        print cmd
    cur.execute(cmd)
    noteId = cur.lastrowid
    for keyword in keywords:
        cmd = "SELECT keywordId FROM keyword WHERE keyword='%s';" % keyword
        if debug:
            print cmd
        cur.execute(cmd)
        keywordId = cur.fetchone()
        if keywordId:
            keywordId = keywordId[0]
        else:
            cmd = "INSERT INTO keyword(keyword) VALUES ('%s');" % keyword
            if debug:
                print cmd
            cur.execute(cmd)
            keywordId = cur.lastrowid
            # FIXME: should check whether the insertion worked
        cmd = "INSERT INTO notekeyword(noteId, keywordID) VALUES(%d, %d)" % (noteId, keywordId)
        if debug:
            print cmd
        cur.execute(cmd)

if args.action == "find":
    noteIds = []
    for keyword in keywords:
        if debug:
            print "keyword:", keyword, "..."
        cmd = "SELECT keywordId FROM keyword WHERE keyword='%s';" % keyword
        if debug:
            print cmd
        cur.execute(cmd)
        keywordId = cur.fetchone()
        if keywordId:
            keywordId = keywordId[0]
            cmd = "SELECT noteId FROM notekeyword where keywordId=%d;" % keywordId
            if debug:
                print cmd
            cur.execute(cmd)
            for noteId in cur.fetchall():
                if debug:
                    print '   ', noteId
                if noteId not in noteIds:
                    noteIds.append(noteId)
        if debug:
            print "noteIds:", noteIds, "\n"
    for n in noteIds:
        cmd = "SELECT noteId, title, content FROM note WHERE noteId=%s;" % n
        if debug:
            print cmd
        cur.execute(cmd)
        res = cur.fetchone()
        print "[%s] %s" % (res[0], res[1])
        print "   ", res[2]

con.commit()
con.close()

