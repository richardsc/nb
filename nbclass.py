#!/usr/bin/python
import sys
import sqlite3 as sqlite
import datetime
import os.path
import json

class Nb:
    def __init__(self, db="nb.db", authorId=1, debug=0):
        '''

        A class used for the storing and searching of textual notes in a
        sqlite3 database.  Keywords may be attached to notes, providing a
        convenient way to search later.

        '''
        if debug:
            print "Working with database named '%s' (before path expansion)." % db
        db = os.path.expanduser(db)
        if debug:
            print "Working with database named '%s' (after path expansion)." % db
        mustInitialize = not os.path.exists(db)
        if mustInitialize:
            print "Warning: there is no database named '%s', so one is being created" % db
        try:
            con = sqlite.connect(db)
        except:
            print "Error opening connection to database named '%s'" % db
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
        self.cur.execute("CREATE TABLE note(noteId integer primary key autoincrement, authorId, date, title, content, privacy DEFAULT 0);")
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
        return noteId

    def delete(self, id=-1):
        if id < 0:
            print "cannot delete a note with a negative id number (%s)" % id
            return False
        if self.debug:
            n = self.cur.execute("SELECT noteId, title FROM note WHERE noteId = ?;", [id])
            print "Deleting the following note:", n.fetchone()
        try:
            self.cur.execute("DELETE FROM note WHERE noteId = ?;", [id])
        except:
            print "there is no note numbered %d" % id
            return False
        try:
            self.cur.execute("DELETE FROM notekeyword WHERE noteId = ?;", [id])
        except:
            print "there was a problem deleting keywords associated with note numbered %d" % id
        self.cleanup()
        self.con.commit()
        return True

    def cleanup(self):
        ''' Clean up the database, e.g. removing unused keywords.'''
        allList = []
        allList.extend(self.cur.execute("SELECT keywordid FROM keyword;"))
        usedList = []
        usedList.extend(self.cur.execute("SELECT keywordid FROM notekeyword;"))
        unusedList = [val for val in allList if val not in usedList]
        for key in unusedList:
            if self.debug:
                print "About to delete keyword with ID %s" % key
            try:
                self.cur.execute("DELETE FROM keyword WHERE keywordId = ?;", key)
            except:
                print "There was a problem deleting keyword %s" % key
        self.con.commit()


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
        rval = []
        for n in noteIds:
            note = self.cur.execute("SELECT noteId, authorId, date, title, content, privacy FROM note WHERE noteId=?;", n).fetchone()
            privacy = note[5]
            keywordIds = []
            keywordIds.extend(self.con.execute("SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = ?;", n))
            keywords = []
            for k in keywordIds:
                keywords.append(self.cur.execute("SELECT keyword FROM keyword WHERE keywordId = ?;", k).fetchone()[0])
            if format == 'json':
                content = note[4].replace('\n', '\\n')
                keywordsStr = ','.join(keywords[i] for i in range(len(keywords)))
                c = {"authorId":note[1], "date":note[2],"title":note[3],"content":content,"privacy":privacy}
                c["keywords"] = keywordsStr
                rval.append({"json":json.dumps(c)})
            else:
                rval.append({"noteId":note[0], "title":note[3], "keywords":keywords,
                    "content":note[4], "privacy":note[5]})
        return rval
