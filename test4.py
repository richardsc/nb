#!/usr/bin/python

'''
python test4.py --tag "lecture,R"
'''

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", type=str, help="comma-separated tags")
args = parser.parse_args()
if args.tag:
    tags = args.tag.split(',')
else:
    print "must give args"
    exit

import sqlite3 as sqlite
import sys

## demonstrate looking up content by tags
filename = "na.db"
#tags = ("lecture", "R")

con = sqlite.connect(filename)
cur = con.cursor()
data_union = ()
for tag in tags:
    cur.execute("select tagid from tag WHERE tag='%s';" % tag)
    tagid = cur.fetchone()[0]
    cur.execute("select note.noteid,title from note LEFT JOIN notetag ON notetag.noteid = note.noteid WHERE notetag.tagid=%s;" % tagid)
    data = cur.fetchall()
    if not len(data_union):
        data_union = data
    else:
        data_union = list(set(data_union) & set(data))

for data in data_union:
    print data

