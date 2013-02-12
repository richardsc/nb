# Idea for a new app (provisionally named 'na')

## Overview

Most of us take notes on lots of things through the day, and would like a way
to store them for a long time, and access them easily hours or years later, by
searching content, looking in date ranges, sifting through tags, etc.  Once
there are more than a few notes, it will become important to be able to edit
them, comment upon them, make links between them, etc.  Notes should be
accessible from a variety of devices, which calls for a cloud-like storage
mechanism.


## Name

Provisionally, call this 'na', for note accumulator.  (Partly, that name is
picked because it is not a unix command.)


## Goals

1. store notes in a database for efficiency and opacity

2. make data available everywhere


## Features

1. ubiquitous

2. update history

3. tags

4. text + graphs

## Input

* from vim

* from commandline


## Development steps

1. Month 1.  By the end of this period, the tool's function and database
   structure should be fairly clear.  Reasonable development steps (perhaps not
in order) are:
  1. The author invites others to think about what such a tool should do,
probably by pointing them at a github development site.
  2. The author develops a few alpha versions as a unix CLI tool, probably
using python and probably using dropbox for ubiquity across platforms.  I till
make sense to dogfood the code (to use the tool to take notes on SQL, for
example).
  3. The author invites other interested parties to think about what sort of
categories of information should be stored in the application.  For example,
the database (as described in a section below) has items called ``tags``.
Maybe it also should have an item called ``priority``, for example.  The first
step is to set up the database with content that will be useful *in practice*,
and not in some abstract sense.  For example, tags really seem to be essential,
so they should definitely go in.
  4. The author starts work on a web version of the tool (probably using django).
2. Month 2: the author invites other unix users to experiment with the CLI or
   web versions of the tool.
3. Later months: mobile versions, the first probably on iphone.


## Some early thoughts on database structure

Rather than explain the idea of the structure, it makes sense to simply provide
the SQL syntax to create and display it.  That way, experienced readers can
make concrete suggestions.

### Set up database

At commandline type

    sqlite3 na.db

to open up a sqlite console on a database named ``an.db``.  (If there is no
such file, it creates one.)

### Add some test content

Cut/paste the following to the sqlite console.

    BEGIN TRANSACTION;
    CREATE TABLE note(noteId integer primary key autoincrement, authorId, date, title, content, views);
    CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);
    CREATE TABLE aliase(aliasId integer primary key autoincrement, item, alias);
    CREATE TABLE tag(tagId integer primary key autoincrement, tag);
    CREATE TABLE notetag(notetagId integer primary key autoincrement, noteid, tagid);
    INSERT INTO author(name, nickname) VALUES ("Dan Kelley", "dk");
    INSERT INTO tag(tag) VALUES ("lecture");
    INSERT INTO tag(tag) VALUES ("R");
    INSERT INTO note (authorId, date, title, content, views) VALUES (1, date('now'), 'John Cook lecture on R', 'http://channel9.msdn.com/Events/Lang-NEXT/Lang-NEXT-2012/Why-and-How-People-Use-R', 0);
    INSERT INTO notetag(noteid, tagid) VALUES (1, 1);
    INSERT INTO notetag(noteid, tagid) VALUES (1, 2);
    INSERT INTO tag(tag) VALUES ("physics");
    INSERT INTO note (authorId, date, title, content, views) VALUES (1, date('now'), 'MIT physics lectures by Water Lewin', 'http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm', 0);
    INSERT INTO notetag(noteid, tagid) VALUES (2, 1);
    INSERT INTO notetag(noteid, tagid) VALUES (2, 3);
    INSERT INTO tag(tag) VALUES ("note aggregator");
    INSERT INTO note (authorId, date, title, content, views) VALUES (1, date('now'), 'need feedback on database categories', 'Asked DB, DI and CR.', 0);
    INSERT INTO notetag(noteid, tagid) VALUES (3, 4);
    COMMIT;

and type control-D to exit the database console.

### See whole database

At the CLI type the following to see the database content.

    echo ".dump" | sqlite3 na.db

### Search for an item

Start an sqlite3 session

    sqlite3 na.db

and then try e.g. as follows

Get IDs of the notes relating to tag number 1 ("lectures")

    select noteid from notetag where tagid=1;

Get the content of all notes tagged 'lecture' (tagid=1)

    select content from note LEFT JOIN notetag ON notetag.noteid = note.noteid WHERE notetag.tagid=1;

Get content of notes tagged 'R' (tagid=2)

    select content from note LEFT JOIN notetag ON notetag.noteid = note.noteid WHERE notetag.tagid=2;

Get content of notes tagged 'lecture' (1) and also 'R' (2)

    FIXME: figure this out

