# Idea for a new open-source note-taking app (provisionally named 'na')

## Overview

Most of us take notes on lots of things through the day, and would like a way
to store them for a long time, and access them easily hours or years later, by
searching content, looking in date ranges, sifting through keywords, etc.  Once
there are more than a few notes, it will become important to be able to edit
them, comment upon them, make links between them, etc.  Notes should be
accessible from a variety of devices, which calls for a cloud-like storage
mechanism.

NB. on apple devices, the cloud is at e.g. (for Preview) ``~/Library/Mobile\
Documents/com~apple~Preview/Documents`` but it's not clear whether special
actions must be undertaken to set up a subdirectory in this area.  Possibly
[this appleinsideer
essay](http://appleinsider.com/articles/11/11/02/hidden_drop_box_feature_in_mac_os_x_lion_lets_you_sync_files_across_macs)
will say more.

## Name

Provisionally, call this ``na``, for note accumulator.  (Partly, that name is
picked because it is not a unix command.)


## Goals

1. store notes in a database for efficiency and opacity

2. make data available everywhere


## Features

1. ubiquitous

2. update history

3. keywords 

4. text + graphs


## Input

* from commandline (this yields the next)

* from vim, emacs etc


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
the database (as described in a section below) has items called ``keywords``.
Maybe it also should have an item called ``priority``, for example.  The first
step is to set up the database with content that will be useful *in practice*,
and not in some abstract sense.  For example, keywords really seem to be essential,
so they should definitely go in.
  4. The author starts work on a web version of the tool (probably using django).
2. Month 2: the author invites other unix users to experiment with the CLI or
   web versions of the tool.
3. Later months: mobile versions, the first probably on iphone.


## Some early thoughts on database structure

Rather than explain the idea of the structure, it makes sense to simply provide
the SQL syntax to create and display it.  That way, experienced readers can
make concrete suggestions.

Note that the following assumes a reader who has downloaded the full contents
of this git repository, and who is able to work in a unix (or linux or osx,
etc.) console.

### Set up database

At commandline type

    sqlite3 na.db

to open up a sqlite console on a database named ``an.db``.  (If there is no
such file, it creates one.)

### Add some test content

Type the following at the unis commandline, to build a database named
``na.db``.

    sqlite3 na.db < make_database.sql

Make sure to do this just once, or to remove the file ``na.db`` before doing
it.  Otherwise, the database will contain duplicated entries.


### See whole database

At the unix commandline, type the following to see the database content.

    echo ".dump" | sqlite3 na.db

### Search for an item

Start an sqlite3 session

    sqlite3 na.db

and then try e.g. as follows

Get IDs of the notes relating to keywords number 1 ("lectures")

    select noteid from notekeyword where keywordId=1;

Get the content of all notes with keyword 'lecture' (keywordId=1)

    select content from note LEFT JOIN notekeyword ON notekeyword.noteid = note.noteid WHERE notekeyword.keywordid=1;

Get content of notes with keyword 'SQL' (keywordId=5)

    select content from note LEFT JOIN notekeyword ON notekeyword.noteid = note.noteid WHERE notekeyword.keywordId=5;

Get content of notes with keywords 'lecture' (1) and also 'R' (2)

    FIXME: figure this out

## Development notes

These notes will probably not be useful to anyone but the developer.  Mostly,
they will name and describe a series of test scripts for creating and working
with the database.  The scripts will generally be orthogonal (testing different
things), with integration of results coming only after the simpler tests have
revealed working methods for isolated tasks.

1. ``test1.py`` tests looking up notes matching keywords in python.  This seems
   preferable to constructing complicated queries, because it will save
learning.  Basically, the idea is to get the logic into a high level language.
Only if this proves to be a bottleneck (for very large databases, perhaps) will
it make a lot of sense to do things in SQL.  So far, ``test1.py`` is not doing
the union operation required for an 'and' on keywords.

2. ``test2.py`` tests an *and* operation between keywords.

3. ``test3.py`` python script to parse commandline flags.

4. ``test4.py`` python script to find notes matching specified keywords.

5. ``test5.py`` python script to add a note.  Try this with e.g. 

        python test5.py --title "an R lecture" --keyword "lecture,R" --content "put content here"

6. ``test6.py`` create keywords if non-extant [supplants ``test5.py``], also do a few other things

        python test6.py --title "oceanpython lecture" --keyword "lecture,python" --content "Diego gave a great talk"

7. ``test7.py`` first trial with a module (a necessary step for web work)

8. ``na.py`` first version that produces useful results.  When major changes to
   this are done, a new ``test*.py`` is created first.  

*To do.* invent an easily-understood syntax for boolean operations on args,
perhaps just e.g.  ``--keyword a+b`` and ``--keyword a|b``.  (It's not good to use
``&`` for logical AND, because that will require escaping in the unix shell.)


## For contributors

To get started, try doing

    make

here, which will create a database (*warning*: it also deletes an existing one!) and then do

    make test

to query that database.
