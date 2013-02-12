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

1. author develops version 1 as a unix CLI tool, perhaps using dropbox for
ubiquity across unix platforms

2. author invites other unix users to experiment (e.g. to see if the
functionality needs adjustment)

3. iphone app

4. other apps


## sql ideas

To get a skeleton of the idea (and to get ideas on what should go in the database) unix CLI users can do as follows.  

## set up database

At commandline type

    sqlite3 an.db

to open up a sqlite console on a database named ``an.db``.

## add some test content

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
    COMMIT;

and type control-D to exit the database console.

## See results

At the CLI type the following to see the database content.

    echo ".dump" | sqlite3 an.db



