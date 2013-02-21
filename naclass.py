#!/usr/bin/python
import sys
import sqlite3 as sqlite
import datetime

class na:
    def __init__(self, filename="na.db", authorId=1, debug=0):
        con = sqlite.connect(filename)
        if not con:
            print "error opening connection"
            sys.exit(1)
        self.con = con
        self.cur = con.cursor()
        self.authorId = authorId
        self.debug = debug 

    def sql(self, cmd, one=False):
        if self.debug:
            print cmd
        self.cur.execute(cmd)
        if one:
            return self.cur.fetchone()
        else:
            return self.cur.fetchall()

    def add(self, title="", keywords="", content="", privacy=0):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        self.sql("INSERT INTO note(authorId, date, title, content, privacy) VALUES(%d, '%s', '%s', '%s', '%s')" %
                (self.authorId, date, title, content, privacy))
        noteId = self.cur.lastrowid
        for keyword in keywords:
            keywordId = self.sql("SELECT keywordId FROM keyword WHERE keyword='%s';" % keyword, one=True)
            if keywordId:
                keywordId = keywordId[0]
            else:
                self.sql("INSERT INTO keyword(keyword) VALUES ('%s');" % keyword)
                keywordId = self.cur.lastrowid
                # FIXME: should check whether the insertion worked
            self.sql("INSERT INTO notekeyword(noteId, keywordID) VALUES(%d, %d)" % (noteId, keywordId))
        self.con.commit()
        self.con.close()
        return(noteId)
   
    def find(self, keywords=""):
        noteIds = []
        if keywords[0] == "?":
            noteIds = self.sql("SELECT noteId from note;")
        else:
            for keyword in keywords:
                if self.debug:
                    print "keyword:", keyword, "..."
                keywordId = self.sql("SELECT keywordId FROM keyword WHERE keyword='%s';" % keyword)[0]
                if keywordId:
                    keywordId = keywordId[0]
                    for noteId in self.sql("SELECT noteId FROM notekeyword WHERE keywordId=%d;" % keywordId):
                        if self.debug:
                            print '   ', noteId
                        if noteId not in noteIds:
                            noteIds.append(noteId)
            if self.debug:
                print "noteIds:", noteIds, "\n"
        for n in noteIds:
            res = self.sql("SELECT noteId, date, title, content, privacy FROM note WHERE noteId=%s;" % n, one=True)
            if int(res[4]) > 0:
                privacy = "(Private)"
            else:
                privacy = "(Public)"
            print "<%s %s> %s %s\n  %s" % (res[0], res[1], res[2], privacy, res[3])
            keys = self.sql("SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = %d;" % n)
            keywords = []
            for k in keys:
                keywords.append(self.sql("SELECT keyword FROM keyword WHERE keywordId = %d;" % k, one=True)[0])
            print " ", ", ".join(keywords[i] for i in range(len(keywords))), "\n"
        self.con.close()

 
