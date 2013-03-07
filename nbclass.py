#!/usr/bin/python
from __future__ import print_function
import sys
import sqlite3 as sqlite
import datetime
import os.path
import json
import difflib
import re
import tempfile
import subprocess

class Nb:
    def __init__(self, db="nb.db", authorId=1, debug=0, quiet=False):
        '''

        A class used for the storing and searching of textual notes in a
        sqlite3 database.  Keywords may be attached to notes, providing a
        convenient way to search later.

        '''
        self.debug = debug 
        self.quiet = quiet
        if debug:
            self.fyi("Working with database named '%s' (before path expansion)." % db)
        db = os.path.expanduser(db)
        if debug:
            self.fyi("Working with database named '%s' (after path expansion)." % db)
        mustInitialize = not os.path.exists(db)
        if mustInitialize:
            self.fyi("Warning: there is no database named '%s', so one is being created" % db)
        try:
            con = sqlite.connect(db)
        except:
            self.error("Error opening connection to database named '%s'" % db)
        self.con = con
        self.cur = con.cursor()
        self.authorId = authorId
        ## 0.3: add note.modified column
        self.appversion = [0, 3]
        self.dbversion = self.appversion
        if mustInitialize:
            self.initialize()
        try:
            v = self.cur.execute("SELECT major,minor FROM version;").fetchone()
            self.dbversion = v
        except:
            self.warning("cannot get version number in database")
            self.dbversion = [0, 0] # started storing version at [0, 1]
            pass
        appversion = int(10*self.appversion[0] + self.appversion[1])
        dbversion = int(10*self.dbversion[0] + self.dbversion[1])
        if debug:
            print("appversion: %d.%d (which translates to %d)" % (self.appversion[0], self.appversion[1], appversion))
            print("dbversion: %d.%d (which translates to %d)" % (self.dbversion[0], self.dbversion[1], dbversion))
        if appversion > dbversion:
            if dbversion < 2:
                self.fyi("Updating the database from version %d.%d to 0.2" % (self.dbversion[0], self.dbversion[1]))
                try:
                    self.cur.execute('ALTER TABLE note ADD due DEFAULT "";')
                    self.fyi("Adding a column named 'due' to the database table named 'note'.")
                except:
                    self.error("Problem adding a column named 'due' to the table 'note'")
                self.con.commit()
            if dbversion < 3:
                self.fyi("Updating the database from version %d.%d to 0.3" % (self.dbversion[0], self.dbversion[1]))
                try:
                    self.cur.execute('ALTER TABLE note ADD modified DEFAULT "";')
                    self.cur.execute('UPDATE note SET modified = date;')
                    self.fyi("Added a column named 'modified' to the database table named 'note'.")
                except:
                    self.error("Problem adding a column named 'modified' to the table named 'note'")
                self.con.commit()
            try:
                self.cur.execute("DELETE FROM version;")
                self.cur.execute("INSERT INTO version(major, minor) VALUES (?,?);",
                        (self.appversion[0], self.appversion[1]))
                self.con.commit()
                self.fyi("Updated the database to version %d.%d" % (self.appversion[0], self.appversion[1]))
            except:
                self.error("Problem updating database version to %d.%d" % (self.appversion[0], self.appversion[1]))


    def fyi(self, msg, prefix="FYI: "):
        if not self.quiet:
            print(prefix + msg, file=sys.stderr)


    def warning(self, msg, prefix="Warning: "):
        if not self.quiet:
            print(prefix + msg, file=sys.stderr)

    def error(self, msg, level=1, prefix="Error: "):
        if not self.quiet:
            print(prefix + msg, file=sys.stderr)
        sys.exit(level)

    def version(self):
        return("Application version %d.%d; database version %d.%d" % (self.appversion[0], self.appversion[1], self.dbversion[0], self.dbversion[1]))

    def initialize(self, author=""):
        ''' Initialize the database.  This is dangerous since it removes any
        existing content.'''
        self.cur.execute("CREATE TABLE version(major, minor);")
        self.cur.execute("INSERT INTO version(major, minor) VALUES (?,?);",
                (self.appversion[0], self.appversion[1]))
        self.cur.execute("CREATE TABLE note(noteId integer primary key autoincrement, authorId, date, modified, title, content, privacy DEFAULT 0);")
        self.cur.execute("CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);")
        self.cur.execute("CREATE TABLE alias(aliasId integer primary key autoincrement, item, alias);")
        self.cur.execute("CREATE TABLE keyword(keywordId integer primary key autoincrement, keyword);")
        self.cur.execute("CREATE TABLE notekeyword(notekeywordId integer primary key autoincrement, noteid, keywordid);")
        self.con.commit()

    def add(self, title="", keywords="", content="", due="", privacy=0, date="", modified=""):
        ''' Add a note to the database.  The title should be short (perhaps 3
        to 7 words).  The keywords are comma-separated, and should be similar
        in style to others in the database.  The content may be of any length.
        Notes with privacy > 0 are increasingly hidden (or will be, when the
        application is more complete). '''

        due = self.interpret_time(due)[0]
        now = datetime.datetime.now()
        if date == "":
            date = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("INSERT INTO note(authorId, date, modified, title, content, privacy, due) VALUES(?, ?, ?, ?, ?, ?, ?);",
                (self.authorId, date, modified, title, content, privacy, due))
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
            self.error("cannot delete a note with a negative id number (%s)" % id)
        if self.debug:
            n = self.cur.execute("SELECT noteId, title FROM note WHERE noteId = ?;", [id])
            print("Deleting the following note:", n.fetchone())
        try:
            self.cur.execute("DELETE FROM note WHERE noteId = ?;", [id])
        except:
            self.error("there is no note numbered %d" % id)
            return False
        try:
            self.cur.execute("DELETE FROM notekeyword WHERE noteId = ?;", [id])
        except:
            self.error("there was a problem deleting keywords associated with note numbered %d" % id)
        self.cleanup()
        self.con.commit()
        return True

    def edit(self, id=-1):
        # BUG: should update modified
        if id < 0:
            self.warning("cannot delete a note with a negative id number (%s)" % id)
        n = self.cur.execute("SELECT title,content,privacy,due,date FROM note WHERE noteId = ?;", [id])
        note = n.fetchone()
        keywords = []
        keywords.extend(self.get_keywords(id))
        ee = self.editor_entry(title=note[0], keywords=keywords, content=note[1], privacy=note[2], due=note[3])
        idnew = self.add(title=ee["title"], keywords=ee["keywords"], content=ee["content"], privacy=ee["privacy"],
                due=ee["due"], date=note[4], modified=datetime.datetime.now())
        self.delete(id) # FIXME: should reuse the noteId
        return idnew

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
                self.error("There was a problem deleting keyword %s" % key)
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
                        self.error("problem finding keyword or note in database")
                        pass
        rval = []
        for n in noteIds:
            try:
                note = self.cur.execute("SELECT noteId, authorId, date, title, content, due, privacy, modified FROM note WHERE noteId=?;", n).fetchone()
            except:
                self.warning("Problem extracting note from database")
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
                        "content":note[4], "due":note[5], "privacy":note[6], "date":note[2], "modified":note[7]})
            else:
                self.error("There is no note numbered %d" % int(n[0]))
        return rval

    def get_keywords(self, id):
        if id < 0:
            self.error("Cannot have a negative note ID")
            return None
        keywordIds = []
        keywordIds.extend(self.con.execute("SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = ?;", [id]))
        keywords = []
        for k in keywordIds:
            keywords.append(self.cur.execute("SELECT keyword FROM keyword WHERE keywordId = ?;", k).fetchone()[0])
        return keywords
 

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
                    else:
                        due = (None, None)
        if self.debug:
            print("due '%s'; tolerance '%s'" % (due[0], due[1]))
        return due


    def editor_entry(self, title, keywords, content, privacy=0, due=""):
        initial_message = '''Instructions: fill in material following the ">" symbol.  (Items following the
"?>" symbol are optional.  The title and keywords must each fit on one line.
Use commas to separate keywords.  The content must start *below* the line
with that title.

TITLE> %s

KEYWORDS> %s

PRIVACY> %s

DUE?> %s

CONTENT...

%s
''' % (title, ",".join(k for k in keywords), privacy, due, content)
        try:
            file = tempfile.NamedTemporaryFile(suffix=".tmp") #, delete=False)
        except:
            self.error('cannot create tempfile')
        file.write(initial_message)
        file.flush()
        #print("tempfile.name: '%s'" % tempfile.name)
        EDITOR = os.environ.get('EDITOR','vi') 
        #print(EDITOR)
        try:
            call([EDITOR, file.name])
        except:
            try:
                os.system(EDITOR + ' ' + file.name)
            except:
                self.error("cannot spawn an editor")
        lines = open(file.name).readlines()
        inContent = False
        content = ""
        for line in lines:
            line = line.rstrip('\n')
            if inContent:
                content = content + line + '\n'
            elif "TITLE" in line:
                title = re.sub(r'.*>', '', line).strip()
            elif "DUE" in line:
                due = re.sub(r'.*>', '', line).strip()
            elif "PRIVACY" in line:
                PRIVACY = re.sub(r'.*>', '', line).strip()
            elif "KEYWORDS" in line:
                keywords = re.sub(r'.*>', '', line).strip()
            elif "CONTENT" in line:
                inContent = True
        content = content.rstrip('\n')
        keywords = keywords.split(',')
        return {"title":title, "keywords":keywords, "content":content, "privacy":privacy, "due":due}

    def find_git_repo(self):
        try:
            out = subprocess.check_output(["git", "remote", "-v"], stderr=subprocess.STDOUT)
            if out:
                o = out.split('\n')
                for repo in o:
                    if "push" in repo:
                        repo = re.compile(r'.*/(.*)\.git.*$').match(repo).group(1)
                        return repo
        except:
            return None
    
