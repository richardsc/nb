#!/usr/bin/python
import sys
import sqlite3 as sqlite
import datetime
import os.path
import json

class Na:
    def __init__(self, db="na.db", authorId=1, debug=0):
        '''

        A class used for the storing and searching of textual notes in a
        sqlite3 database.  Keywords may be attached to notes, providing a
        convenient way to search later.

        '''
        db = os.path.expanduser(db)
        if debug:
            print "db: '%s' (after path expansion)" % db
        mustInitialize = not os.path.exists(db)
        if debug:
            print 'mustInitialize:', mustInitialize
        con = sqlite.connect(db)
        if not con:
            print "error opening connection"
            sys.exit(1)
        self.con = con
        self.cur = con.cursor()
        self.authorId = authorId
        self.debug = debug 
        if mustInitialize:
            self.initialize()

    def initialize(self, author=""):
        ''' Initialize the database.  This is dangerous since it removes any
        existing content.'''
        self.cur.execute("CREATE TABLE note(noteId integer primary key autoincrement, authorId, date, title, content, privacy DEFAULT 0, views DEFAULT 0);")
        self.cur.execute("CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);")
        self.cur.execute("CREATE TABLE alias(aliasId integer primary key autoincrement, item, alias);")
        self.cur.execute("CREATE TABLE keyword(keywordId integer primary key autoincrement, keyword);")
        self.cur.execute("CREATE TABLE notekeyword(notekeywordId integer primary key autoincrement, noteid, keywordid);")

    def add(self, title="", keywords="", content="", privacy=0):
        ''' Add a note to the database.  The title should be short (perhaps 3
        to 7 words).  The keywords are comma-separated, and should be similar
        in style to others in the database.  The content may be of any length.
        Notes with privacy > 0 are increasingly hidden (or will be, when the
        application is more complete). '''
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("INSERT INTO note(authorId, date, title, content, privacy) VALUES(?, ?, ?, ?, ?);",
                (self.authorId, date, title, content, privacy))
        noteId = self.cur.lastrowid
        for keyword in keywords:
            if self.debug:
                print " inserting keyword:", keyword
            keywordId = self.con.execute("SELECT keywordId FROM keyword WHERE keyword = ?;", [keyword]).fetchone()
            if keywordId:
                if self.debug:
                    print "(existing keyword with id:", keywordId, ")"
                keywordId = keywordId[0]
            else:
                if self.debug:
                    print "(new keyword)"
                self.cur.execute("INSERT INTO keyword(keyword) VALUES (?);", [keyword])
                keywordId = self.cur.lastrowid
            self.con.execute("INSERT INTO notekeyword(noteId, keywordID) VALUES(?, ?)", [noteId, keywordId])
        self.con.commit()
        return(noteId)
   
    def find(self, keywords="", format="plain"):
        '''Search notes for a given keyword, printing the results in either
        'text' or 'json' format.'''
        noteIds = []
        if keywords[0] == "?":
            noteIds.extend(self.con.execute("SELECT noteId FROM note;"))
        else:
            for keyword in keywords:
                if self.debug:
                    print "keyword:", keyword, "..."
                keywordId = self.cur.execute("SELECT keywordId FROM keyword WHERE keyword = ?;", [keyword])
                try:
                    keywordId = self.con.execute("SELECT keywordId FROM keyword WHERE keyword = ?;", [keyword]).fetchone()
                    if keywordId:
                        for noteId in self.cur.execute("SELECT noteId FROM notekeyword WHERE keywordId = ?;", keywordId):
                            if self.debug:
                                print '  noteId:', noteId
                            if noteId not in noteIds:
                                noteIds.append(noteId)
                except:
                    print "problem"
                    pass
        for n in noteIds:
            res = self.cur.execute("SELECT noteId, authorId, date, title, content, privacy FROM note WHERE noteId=?;", n).fetchone()
            privacy = res[5]
            #print "<%s %s> %s" % (res[0], res[1], privacy),
            keywordIds = []
            keywordIds.extend(self.con.execute("SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = ?;", n))
            keywords = []
            for k in keywordIds:
                keywords.append(self.cur.execute("SELECT keyword FROM keyword WHERE keywordId = ?;", k).fetchone()[0])
            if format == 'json':
                # >>> json.loads('{"c":"ab \\n \' \\" c"}')
                # {u'c': u'ab \n \' " c'}
                content = res[4]
                content = res[4].replace('\n', '\\n')
                ##content = content.replace('"', '\\"')
                ##content = content.replace("'", "\'")
                #print '{"authorId":"%s","date":"%s","title":"%s","content":"%s","privacy":"%s","keywords":"' % (res[1], res[2], res[3], content, privacy),
                #print ','.join(keywords[i] for i in range(len(keywords))), '"}'
                keywordsStr = ','.join(keywords[i] for i in range(len(keywords)))
                c = {"authorId":res[1], "date":res[2],"title":res[3],"content":content,"privacy":privacy}
                c["keywords"] = keywordsStr
                print json.dumps(c)
            else:
                print "\"%s\"" % res[3],
                print "[", " ] [ ".join(keywords[i] for i in range(len(keywords))), "]"
                content = res[4].replace('\\n', '\n')
                for contentLine in content.split('\n'):
                    print "  ", contentLine
                print '\n'
