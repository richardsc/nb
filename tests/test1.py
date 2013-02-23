#!/usr/bin/python

# some refs I consulted, with the best given first:
# http://docs.python.org/2/library/sqlite3.html
# http://zetcode.com/db/sqlitepythontutorial/

import sqlite3 as sqlite
import sys

## demonstrate looking up content by (a single) tag
filename = "na.db"
tags = ("lecture", "R")

con = sqlite.connect(filename)
cur = con.cursor()
for tag in tags:
    cur.execute("select tagid from tag WHERE tag='%s';" % tag)
    tagid = cur.fetchone()[0]
    cur.execute("select note.noteid,content from note LEFT JOIN notetag ON notetag.noteid = note.noteid WHERE notetag.tagid=%s;" % tagid)
    data = cur.fetchall()
    print "tag: '%s' has tagged the following notes (id, content)" % tag
    for d in data:
        print(d)
    print '\n'

