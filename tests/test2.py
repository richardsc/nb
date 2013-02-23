#!/usr/bin/python

import sqlite3 as sqlite
import sys

## demonstrate looking up content by tags
filename = "na.db"
tags = ("lecture", "R")

con = sqlite.connect(filename)
cur = con.cursor()
data_union = ()
for tag in tags:
    cur.execute("select tagid from tag WHERE tag='%s';" % tag)
    tagid = cur.fetchone()[0]
    cur.execute("select note.noteid,content from note LEFT JOIN notetag ON notetag.noteid = note.noteid WHERE notetag.tagid=%s;" % tagid)
    data = cur.fetchall()
    if not len(data_union):
        data_union = data
    else:
        data_union = list(set(data_union) & set(data))
    print "notes matching tag '%s' (id, content)" % tag
    for d in data:
        print(d)
    print '\n'

print 'Notes matching all tags:\n'
print data_union

