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

    def add(self, title, keywords, content, privacy=0):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        cmd = "INSERT INTO note(authorId, date, title, content, privacy) VALUES(%d, '%s', '%s', '%s', '%s')" % (self.authorId, date, title, content, privacy)
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
        return(noteId)
   
    def find(self, keywords):
        noteIds = []
        if keywords[0] == "?":
            cmd = "SELECT noteId FROM note;"
            if self.debug:
                print cmd
            self.cur.execute(cmd)
            noteIds = self.cur.fetchall()
        else:
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
            if int(res[4]) > 0:
                privacy = "(Private)"
            else:
                privacy = "(Public)"
            print "<%s %s> %s %s\n  %s" % (res[0], res[1], res[2], privacy, res[3])
            # Next bit should be done with a join, I think
            cmd = "SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = %d" % n
            if self.debug:
                print cmd
            self.cur.execute(cmd)
            keys = self.cur.fetchall()
            keywords = []
            for k in keys:
                cmd = "SELECT keyword FROM keyword WHERE keywordid = %d" % k
                if self.debug:
                    print cmd
                self.cur.execute(cmd)
                keywords.append(self.cur.fetchone()[0])
            print " ", ", ".join(keywords[i] for i in range(len(keywords))), "\n"
        self.con.close()

 
