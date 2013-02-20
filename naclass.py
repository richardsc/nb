#!/usr/bin/python
import sys
import sqlite3 as sqlite
import datetime

class na:
    def __init__(self, filename="na.db", authorId=1, debug=0):
        con = sqlite.connect(filename)
        if not con:
            print "error opening connection"
            exit(1)
        self.con = con
        self.cur = con.cursor()
        self.authorId = authorId
        self.debug = debug 

    def add(self, title, keywords, content):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        cmd = "INSERT INTO note(authorId, date, title, content) VALUES(%d, '%s', '%s', '%s')" % (self.authorId, date, title, content)
        if self.debug:
            print cmd
        self.cur.execute(cmd)
        noteId = self.cur.lastrowid
        for keyword in keywords:
            cmd = "SELECT keywordId FROM keyword WHERE keyword='%s';" % keyword
            if self.debug:
                print cmd
            self.cur.execute(cmd)
            keywordId = self.cur.fetchone()
            if keywordId:
                keywordId = keywordId[0]
            else:
                cmd = "INSERT INTO keyword(keyword) VALUES ('%s');" % keyword
                if self.debug:
                    print cmd
                self.cur.execute(cmd)
                keywordId = self.cur.lastrowid
                # FIXME: should check whether the insertion worked
            cmd = "INSERT INTO notekeyword(noteId, keywordID) VALUES(%d, %d)" % (noteId, keywordId)
            if self.debug:
                print cmd
            self.cur.execute(cmd)
        self.con.commit()
        self.con.close()
   
    def find(self, keywords):
        noteIds = []
        for keyword in keywords:
            if self.debug:
                print "keyword:", keyword, "..."
            cmd = "SELECT keywordId FROM keyword WHERE keyword='%s';" % keyword
            if self.debug:
                print cmd
            self.cur.execute(cmd)
            keywordId = self.cur.fetchone()
            if keywordId:
                keywordId = keywordId[0]
                cmd = "SELECT noteId FROM notekeyword where keywordId=%d;" % keywordId
                if self.debug:
                    print cmd
                self.cur.execute(cmd)
                for noteId in self.cur.fetchall():
                    if self.debug:
                        print '   ', noteId
                    if noteId not in noteIds:
                        noteIds.append(noteId)
            if self.debug:
                print "noteIds:", noteIds, "\n"
        for n in noteIds:
            cmd = "SELECT noteId, date, title, content, privacy FROM note WHERE noteId=%s;" % n
            if self.debug:
                print cmd
            self.cur.execute(cmd)
            res = self.cur.fetchone()
            if res[4]:
                privacy = "(Private)"
            else:
                privacy = ""
            print "<%s %s> %s %s" % (res[0], res[1], res[2], privacy)
            print "   ", res[3]
        self.con.close()
 
