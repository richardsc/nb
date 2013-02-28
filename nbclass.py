#!/usr/bin/python
from __future__ import print_function
import sys
import sqlite3 as sqlite
import datetime
import os.path
import json
import difflib
import re

class Nb:
    def __init__(self, db="nb.db", authorId=1, debug=0):
        '''

        A class used for the storing and searching of textual notes in a
        sqlite3 database.  Keywords may be attached to notes, providing a
        convenient way to search later.

        '''
        if debug:
            print("Working with database named '%s' (before path expansion)." % db)
        db = os.path.expanduser(db)
        if debug:
            print("Working with database named '%s' (after path expansion)." % db)
        mustInitialize = not os.path.exists(db)
        if mustInitialize:
            print("Warning: there is no database named '%s', so one is being created" % db)
        try:
            con = sqlite.connect(db)
        except:
            print("Error opening connection to database named '%s'" % db)
            sys.exit(1)
        self.con = con
        self.cur = con.cursor()
        self.authorId = authorId
        self.debug = debug 
        self.appversion = [0, 2]
        self.dbversion = self.appversion
        if mustInitialize:
            self.initialize()
        try:
            v = self.cur.execute("SELECT major,minor FROM version;").fetchone()
            self.dbversion = v
        except:
            print("cannot get version number in database")
            self.dbversion = [0, 0] # started storing version at [0, 1]
            pass
        appversion = 10*self.appversion[0] + self.appversion[1]
        dbversion = 10*self.dbversion[0] + self.dbversion[1]
        if debug:
            print("appversion: %d.%d" % (self.appversion[0], self.appversion[1]))
            print("dbversion: %d.%d" % (self.dbversion[0], self.dbversion[1]))
        if appversion > dbversion: # FIXME: this only works for versions 0.1 and 0.2
            print("Updating the database from version %d.%d to %d.%d" % (self.dbversion[0], self.dbversion[1], self.appversion[0], self.appversion[1]))
            try:
                self.cur.execute('ALTER TABLE note ADD due DEFAULT "";')
                print("Adding a column named 'due' to the database table named 'note'.")
            except:
                print("Problem adding the 'due' column to the table 'note'")
            self.con.commit()
            try:
                self.cur.execute("DELETE FROM version;")
                self.cur.execute("INSERT INTO version(major, minor) VALUES (?,?);",
                        (self.appversion[0], self.appversion[1]))
                print("Updating the database table 'version' to value", self.appversion)
            except:
                print("Problem updating database version to %d.%d" % (self.appversion[0], self.appversion[1]))
            self.con.commit()



    def version(self):
        print("Application version %d.%d; database version %d.%d" % (self.appversion[0], self.appversion[1], self.dbversion[0], self.dbversion[1]))

    def initialize(self, author=""):
        ''' Initialize the database.  This is dangerous since it removes any
        existing content.'''
        self.cur.execute("CREATE TABLE version(major, minor);")
        self.cur.execute("INSERT INTO version(major, minor) VALUES (?,?);",
                (self.appversion[0], self.appversion[1]))
        self.cur.execute("CREATE TABLE note(noteId integer primary key autoincrement, authorId, date, title, content, privacy DEFAULT 0);")
        self.cur.execute("CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);")
        self.cur.execute("CREATE TABLE alias(aliasId integer primary key autoincrement, item, alias);")
        self.cur.execute("CREATE TABLE keyword(keywordId integer primary key autoincrement, keyword);")
        self.cur.execute("CREATE TABLE notekeyword(notekeywordId integer primary key autoincrement, noteid, keywordid);")
        self.con.commit()

    def add(self, title="", keywords="", content="", due="", privacy=0):
        ''' Add a note to the database.  The title should be short (perhaps 3
        to 7 words).  The keywords are comma-separated, and should be similar
        in style to others in the database.  The content may be of any length.
        Notes with privacy > 0 are increasingly hidden (or will be, when the
        application is more complete). '''

        due = self.interpret_time(due)[0]
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("INSERT INTO note(authorId, date, title, content, privacy, due) VALUES(?, ?, ?, ?, ?, ?);",
                (self.authorId, date, title, content, privacy, due))
        noteId = self.cur.lastrowid
        for keyword in keywords:
            if self.debug:
                print(" inserting keyword:", keyword)
            keywordId = self.con.execute("SELECT keywordId FROM keyword WHERE keyword = ?;", [keyword]).fetchone()
            if keywordId:
                if self.debug:
                    print("(existing keyword with id:", keywordId, ")")
                keywordId = keywordId[0]
            else:
                if self.debug:
                    print("(new keyword)")
                self.cur.execute("INSERT INTO keyword(keyword) VALUES (?);", [keyword])
                keywordId = self.cur.lastrowid
            self.con.execute("INSERT INTO notekeyword(noteId, keywordID) VALUES(?, ?)", [noteId, keywordId])
        self.con.commit()
        return noteId

    def delete(self, id=-1):
        if id < 0:
            print("cannot delete a note with a negative id number (%s)" % id)
            return False
        if self.debug:
            n = self.cur.execute("SELECT noteId, title FROM note WHERE noteId = ?;", [id])
            print("Deleting the following note:", n.fetchone())
        try:
            self.cur.execute("DELETE FROM note WHERE noteId = ?;", [id])
        except:
            print("there is no note numbered %d" % id)
            return False
        try:
            self.cur.execute("DELETE FROM notekeyword WHERE noteId = ?;", [id])
        except:
            print("there was a problem deleting keywords associated with note numbered %d" % id)
        self.cleanup()
        self.con.commit()
        return True

    def edit(self, id=-1):
        if id < 0:
            print("cannot delete a note with a negative id number (%s)" % id)
        print("BUG: 'nb edit --id %d' does not work yet" % id)# FIXME: use similar to 'add'

    def cleanup(self):
        ''' Clean up the database, e.g. removing unused keywords.'''
        allList = []
        allList.extend(self.cur.execute("SELECT keywordid FROM keyword;"))
        usedList = []
        usedList.extend(self.cur.execute("SELECT keywordid FROM notekeyword;"))
        unusedList = [val for val in allList if val not in usedList]
        for key in unusedList:
            if self.debug:
                print("About to delete keyword with ID %s" % key)
            try:
                self.cur.execute("DELETE FROM keyword WHERE keywordId = ?;", key)
            except:
                print("There was a problem deleting keyword %s" % key)
        self.con.commit()


    def find(self, id=None, keywords="", mode="plain", strict=False):
        '''Search notes for a given id or keyword, printing the results in
        either 'plain' or 'JSON' format.'''
        noteIds = []
        if id:
            noteIds.append([id])
        else:
            if keywords[0] == "?":
                noteIds.extend(self.con.execute("SELECT noteId FROM note;"))
            else:
                if not strict:
                    keywordsKnown = []
                    for k in self.cur.execute("SELECT keyword FROM keyword;").fetchall():
                        keywordsKnown.extend(k)
                    keywordsFuzzy = difflib.get_close_matches(keywords[0], keywordsKnown, n=1, cutoff=0.6) # FIXME: multiple keywords
                    if len(keywordsFuzzy) > 0:
                        keywords = [keywordsFuzzy[0]]
                for keyword in keywords:
                    if self.debug:
                        print("keyword:", keyword, "...")
                    keywordId = self.cur.execute("SELECT keywordId FROM keyword WHERE keyword = ?;", [keyword])
                    try:
                        keywordId = self.con.execute("SELECT keywordId FROM keyword WHERE keyword = ?;", [keyword]).fetchone()
                        if keywordId:
                            for noteId in self.cur.execute("SELECT noteId FROM notekeyword WHERE keywordId = ?;", keywordId):
                                if self.debug:
                                    print('  noteId:', noteId)
                                if noteId not in noteIds:
                                    noteIds.append(noteId)
                    except:
                        print("problem finding keyword or note in database")
                        pass
        rval = []
        for n in noteIds:
            try:
                note = self.cur.execute("SELECT noteId, authorId, date, title, content, due, privacy FROM note WHERE noteId=?;", n).fetchone()
            except:
                print("Problem extracting note from database")
                next
            if note:
                privacy = note[6]
                keywordIds = []
                keywordIds.extend(self.con.execute("SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = ?;", n))
                keywords = []
                for k in keywordIds:
                    keywords.append(self.cur.execute("SELECT keyword FROM keyword WHERE keywordId = ?;", k).fetchone()[0])
                if mode == 'json':
                    content = note[4].replace('\n', '\\n')
                    keywordsStr = ','.join(keywords[i] for i in range(len(keywords)))
                    c = {"authorId":note[1], "date":note[2],"title":note[3],"content":content,"privacy":privacy}
                    c["keywords"] = keywordsStr
                    rval.append({"json":json.dumps(c)})
                else:
                    rval.append({"noteId":note[0], "title":note[3], "keywords":keywords,
                        "content":note[4], "due":note[5], "privacy":note[6]})
            else:
                print("There is no note numbered %d." % n[0])
        return rval

    def interpret_time(self, due):
        # catch "tomorrow" and "Nhours", "Ndays", "Nweeks" (with N an integer)
        now = datetime.datetime.now()
        sperday = 86400
        if due == "today":
            due = (now, sperday)
        elif due == "tomorrow":
            due = (now + datetime.timedelta(days=1), sperday)
        else:
            ## try hours, then days, then weeks.
            test = re.compile(r'(\d+)([ ]*hour)(s*)').match(due)
            if test:
                due = (now + datetime.timedelta(hours=int(test.group(1))), sperday/24)
            else:
                test = re.compile(r'(\d+)([ ]*day)(s*)').match(due)
                if test:
                    due = (now + datetime.timedelta(days=int(test.group(1))), sperday/1)
                else:
                    test = re.compile(r'(\d+)([ ]*week)(s*)').match(due)
                    if test:
                        due = (now + datetime.timedelta(weeks=int(test.group(1))), sperday*7)
                        #print("decoded weeks")
                    else:
                        due = (None, None)
        if self.debug:
            print("due '%s'; tolerance '%s'" % (due[0], due[1]))
        return due

