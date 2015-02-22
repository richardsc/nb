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
import hashlib

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
        self.appversion = [0, 4]
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
                self.fyi("Updating the database from version %d.%d to 0.2 ..." % (self.dbversion[0], self.dbversion[1]))
                try:
                    self.cur.execute('ALTER TABLE note ADD due DEFAULT "";')
                    self.fyi("  Adding a column named 'due' to the database table named 'note'.")
                except:
                    self.error("  Problem adding a column named 'due' to the table 'note'")
                self.con.commit()
            if dbversion < 3:
                self.fyi("Updating the database from version %d.%d to 0.3 ..." % (self.dbversion[0], self.dbversion[1]))
                try:
                    self.cur.execute('ALTER TABLE note ADD modified DEFAULT "";')
                    self.cur.execute('UPDATE note SET modified = date;')
                    self.fyi("  Added a column named 'modified' to the database table named 'note'.")
                except:
                    self.error("  Problem adding a column named 'modified' to the table named 'note'")
                self.con.commit()
            if dbversion < 4:
                self.fyi("Updating the database from version %d.%d to 0.4 ..." % (self.dbversion[0], self.dbversion[1]))
                try:
                    cmd = 'ALTER TABLE note ADD hash DEFAULT "";'
                    self.cur.execute(cmd)
                    self.con.commit()
                    cmd = "SELECT noteId,date,title FROM note;"
                    self.cur.execute(cmd)
                    id = []
                    hash = []
                    while True:
                        row = self.cur.fetchone()
                        if row == None:
                            break
                        id.append(row[0])
                        h = hashlib.sha256(row[1]+row[2]).hexdigest()
                        hash.append(h)
                    if self.debug:
                        print(id)
                        print(hash)
                    for i in range(len(id)):
                        if self.debug:
                            print("i:", i)
                            print("UPDATE note SET hash = \"%s\" WHERE noteId=%s;" % (hash[i], id[i]))
                        self.cur.execute("UPDATE note SET hash = ? WHERE noteId=?;", (hash[i], id[i]))
                    self.con.commit()
                    self.fyi("  Added a column named 'hash' to the database table named 'note'.")
                except:
                    self.error("  Problem adding a column named 'hash' to the table named 'note'")
            try:
                self.cur.execute("DELETE FROM version;")
                self.cur.execute("INSERT INTO version(major, minor) VALUES (?,?);",
                        (self.appversion[0], self.appversion[1]))
                self.con.commit()
                self.fyi("Updated the database to version %d.%d" % (self.appversion[0], self.appversion[1]))
            except:
                self.error("  Problem updating database version to %d.%d" % (self.appversion[0], self.appversion[1]))


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
        self.cur.execute("CREATE TABLE note(noteId integer primary key autoincrement, authorId, date, modified, due, title, content, hash, privacy DEFAULT 0);")
        self.cur.execute("CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);")
        self.cur.execute("CREATE TABLE alias(aliasId integer primary key autoincrement, item, alias);")
        self.cur.execute("CREATE TABLE keyword(keywordId integer primary key autoincrement, keyword);")
        self.cur.execute("CREATE TABLE notekeyword(notekeywordId integer primary key autoincrement, noteid, keywordid);")
        self.con.commit()

    def add(self, title="", keywords="", content="", due="", privacy=0, date="", modified="", hash=""):
        ''' Add a note to the database.  The title should be short (perhaps 3
        to 7 words).  The keywords are comma-separated, and should be similar
        in style to others in the database.  The content may be of any length.
        Notes with privacy > 0 are increasingly hidden (or will be, when the
        application is more complete). '''
        title = title.decode('utf-8')
        content = content.decode('utf-8')
        due = self.interpret_time(due)[0]
        now = datetime.datetime.now()
        if date == "":
            date = now.strftime("%Y-%m-%d %H:%M:%S")
        if not len(hash):
            hash = hashlib.sha256(date+title).hexdigest()
        self.cur.execute("INSERT INTO note(authorId, date, modified, title, content, privacy, due, hash) VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
                (self.authorId, date, modified, title, content, privacy, due, hash))
        noteId = self.cur.lastrowid
        for keyword in keywords:
            keyword = keyword.decode('utf-8')
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
        # Edit a note, avoiding code repetition by making a new one and then renumbering it
        if id < 0:
            self.warning("cannot delete a note with a negative id number (%s)" % id)
        old = self.find(id)
        if 1 != len(old):
            self.error("hash matches %s notes; try adding a character" % len(old))
        old = old[0]
        print(old)
        print("noteId %s" % old['noteId'])
        print("hash %s" % old['hash'])
        keywords = []
        keywords.extend(self.get_keywords(old['noteId']))
        print(keywords)
        ee = self.editor_entry(title=old['title'], keywords=keywords, content=old['content'], privacy=old['privacy'], due=old['due'])
        # the hash never changes
        idnew = self.add(title=ee["title"], keywords=ee["keywords"], content=ee["content"], privacy=ee["privacy"],
                due=ee["due"], date=old['date'], modified=datetime.datetime.now(), hash=old["hash"])
        self.delete(old['noteId'])
        try:
            if self.debug:
                self.fyi("UPDATE notekeyword SET noteId=%d WHERE noteId=%d;" % (old['noteId'], idnew))
            self.cur.execute("UPDATE notekeyword SET noteId=? WHERE noteId=?;", (old['noteId'], idnew))
        except:
            self.error("cannot update notekeyword database to reflect reassignment of temporary note %d as %d", (idnew, id))
        #try:
        #    if self.debug:
        #        self.fyi("UPDATE note SET noteId=%d WHERE noteId=%d;" % (old['noteId'], idnew))
        #    print("OLD id %s" % old['noteId'])
        #    print("NEW id %s" % idnew)
        #    self.cur.execute("UPDATE note SET noteId=? WHERE noteId=?;", (old['noteId'], idnew))
        #except:
        #    self.error("cannot update note database to reflect reassignment of temporary note %d as %d" % (idnew, old['noteId']))
        self.con.commit()
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

    def get_id_list(self):
        '''Return list of ID values'''
        noteIds = []
        noteIds.extend(self.con.execute("SELECT noteId FROM note;"))
        return(noteIds)

    def find(self, id=None, keywords="", mode="plain", strict=False):
        '''Search notes for a given id or keyword, printing the results in
        either 'plain' or 'JSON' format.'''
        noteIds = []
        if id:
            if self.debug:
                print("id: %s" % id[0:1])
        if id and "-" != id[0:1]:
            noteIds.append([id])
        else:
            if self.debug:
                print("len(keywords) %s" % len(keywords))
            if 0 == len(keywords) or keywords[0] == "?":
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
        ## convert from hash to ids. Note that one hash may create several ids.
        noteIds2 = []
        if self.debug:
            print("ORIGINALLY: %s" % noteIds)
        for n in noteIds:
            #print("START n=%s" % n)
            #print("n: %s" % n[0])
            if isinstance(n[0], str):
                if self.debug:
                    print("STR %s" % n)
                rows = self.cur.execute("SELECT noteId, hash FROM note;").fetchall()
                #print(rows)
                l = len(n[0])
                for r in rows:
                    if n[0] == r[1][0:l]:
                        noteIds2.append((r[0],))
            else:
                noteIds2.append(n)
        if len(noteIds2):
            noteIds = noteIds2
        if self.debug:
            print("LATER: %s" % noteIds)
        rval = []
        if self.debug:
            print(noteIds)
        for n in noteIds:
            if self.debug:
                print("check n %s" % n)
            try:
                note = self.cur.execute("SELECT noteId, authorId, date, title, content, due, privacy, modified, hash FROM note WHERE noteId=?;", n).fetchone()
            except:
                self.warning("Problem extracting note from database")
                next
            if note:
                date = note[2]
                due = note[5]
                privacy = note[6]
                keywordIds = []
                keywordIds.extend(self.con.execute("SELECT keywordid FROM notekeyword WHERE notekeyword.noteid = ?;", n))
                keywords = []
                for k in keywordIds:
                    keywords.append(self.cur.execute("SELECT keyword FROM keyword WHERE keywordId = ?;", k).fetchone()[0])
                if mode == 'json':
                    content = note[4].replace('\n', '\\n')
                    keywordsStr = ','.join(keywords[i] for i in range(len(keywords)))
                    c = {"authorId":note[1], "date":date,"due":due,"title":note[3],"content":content,"privacy":privacy}
                    c["keywords"] = keywordsStr
                    rval.append({"json":json.dumps(c)})
                else:
                    rval.append({"noteId":note[0], "title":note[3], "keywords":keywords,
                        "content":note[4], "due":note[5], "privacy":note[6],
                        "date":note[2], "modified":note[7], "hash":note[8]})
            else:
                self.error("There is no note with abbreviated hash '%s'" % n[0])
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
        remaining = None
        if due:
            now = datetime.datetime.now()
            #print("due: %s" % due)
            #print(due)
            DUE = datetime.datetime.strptime(due, "%Y-%m-%d %H:%M:%S.%f")
            remaining = (DUE - now).total_seconds()
            #print("remaining: %s" % remaining)
            if (abs(remaining) < 86400):
                remaining = "%d hours" % round(remaining / 3600)
            else:
                remaining = "%d days" % round(remaining / 86400)
            #print("remaining: %s" % remaining)
            due = remaining
        initial_message = '''Instructions: fill in material following the ">" symbol.  (Items following the
"?>" symbol are optional.  The title and keywords must each fit on one line.
Use commas to separate keywords.  The content must start *below* the line
with that title.

TITLE> %s

KEYWORDS> %s

PRIVACY> %s

DUE (E.G. 'tomorrow' or '3 days')> %s

CONTENT...
%s
''' % (title, ",".join(k for k in keywords), privacy, due, content)
        try:
            file = tempfile.NamedTemporaryFile(suffix=".tmp") #, delete=False)
        except:
            self.error('cannot create tempfile')
        file.write(initial_message.encode('utf-8'))
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

    #def find_git_repo(self):
    #    try:
    #        out = subprocess.check_output(["git", "remote", "-v"], stderr=subprocess.STDOUT)
    #        if out:
    #            o = out.split('\n')
    #            for repo in o:
    #                if "push" in repo:
    #                    repo = re.compile(r'.*/(.*)\.git.*$').match(repo).group(1)
    #                    return repo
    #    except:
    #        return None
   
    def rename_keyword(self, old, new):
        if self.debug:
            self.fyi("UPDATE keyword SET keyword=\"%s\" WHERE keyword=\"%s\";" % (new, old))
        try:
            self.cur.execute("UPDATE keyword SET keyword = ? WHERE keyword = ?;", (new, old))
        except:
            self.error("cannot change keyword from '%s' to '%s'" % (old, new))
        try:
            self.con.commit()
        except:
            self.error("cannot commit the database after changing keyword from '%s' to '%s'" % (old, new))

