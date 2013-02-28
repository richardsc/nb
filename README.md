## Abstract

'nb' is an open-source application for recording textual notes and associated
meta-information that may be used for later retrieval.

## Overview

Most people find it helpful to store notes on a computer.  Some use specialized
applications for this, while others prefer the simplicity of recording their
thoughts in a plain-text file, using a familiar text editor.  In this second
option, it is common to associate the text files with projects or tasks.
Depending on the intent, the file might be named "README" or perhaps something
more meaningful, such as "PLANS," "TASKS," "BUGS," "IDEAS," etc.  Thus, for M
projects and N categories, there might be M x N files, and the handling of all
those files can grow complicated, whether adding new material or finding old
material.

A reasonable solution is to have a single file, in which notes can be stored
along with meta-information, such as keywords.  For example, plans for a
project named "foo" might be flagged with the keywords *foo* and *plans*, and
retrieving those plans would be a simple matter of filtering on those keywords.

Storing notes along with keywords (and other meta-information, such as the
date, the author, etc.) is somewhat complicated in a text file that is to be
edited with a general text editor, not least because a typo might damage the
file.  Storing notes in a database is a good solution to this problem, and it
offers the additional advantage of greatly improved lookup speed.  The
disadvantage of the database, however, is that an application is required to
act as an interface between the user and the data.  If the application is
commercial, then users expose themselves to the risk of losing all their work,
if the company stops supporting the software.

The ``nb`` application (named for the Latin phrase "nota bene") is designed
with all these things in mind.  It is deliberately restricted in its features,
focussing on the creation of textual notes and their retrieval.  Complex
formatting is not provided, nor is the ability to add non-textual material.  In
the present early version, ``nb`` functions entirely at the unix command line,
and is most suited for power users who are unafraid of that environment.

The development model for ``nb`` is entirely open-source, and the coding relies
on popular tools that will be familiar to many programmers, mitigating against
obsolescence. 

## Development timeline

### 2013-02

* Develop a series of trial versions that will be suitable for use by the
  author in his own work.

* Tell others of the project and invite discussion of features (especially
  database design).

### 2013-03

* Based on experience in everyday use, firm up the database design.

* Invite other developers to work on editor-based versions.

* Develop a trial web-based version.


## Using nb

### Installation

Download the source code to some directory, and then create an alias along the
following lines, adjusted for the directory name

    alias nb=/Users/kelley/src/nb/nb

### Specifying a database file

The default database file is ``~/Dropbox/nb.db``, but this may not suit all
users, so there are two ways to specify a different file.  The first way is to
supply the filename as an argument, e.g. ``nb find --db ~/nb.db``.  The second
way is to name a default database in an initialization file named ``~/.nbrc``;
for example it might contain the following.

    db = "~/Dropbox/nb.db"

### Create a database

    ./nb RESET

Important: this will erase an existing database.


### Add notes

This may be done one at a time, with commandline arguments, e.g.

    ./nb add --keywords 'lecture,physics,MIT' --title="Walter Lewin physics lectures" --content="http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm"

Another method is with an editor-based supply of the information, which is done
unless ``--keywords``, ``--title``, and ``--content`` are all given, e.g.

    ./nb add

or

    ./nb add --title "a new note"

One or more notes can also be added through input of a JSON file, e.g.

    ./nb add --mode json --file note.json

### Find notes

At present, the only way to find notes is by searching for a keyword, e.g.

    ./nb find --keyword "lecture"

Note that the search is fuzzy, so that e.g. "leture" would get the same results
as "lecture".  However, this scheme can have surprising results, so the
``--strict`` commandline argument is provided, to do strict searches.

To get all the notes, use

    ./nb find

To find a note with a given ID, use e.g.

    ./nb find --id 1


### Export notes

Notes may be exported to a JSON file by e.g.

    ./nb find --mode json > notes.json

or probably more usefully, in plain format by e.g.

    ./nb find --id 1 > note_1.txt

to extract the note with the stated ID, or e.g.

    ./nb find --key arctic > note_arctic.txt

to extract notes with keyword "arctic".

## Import notes

An individual note (e.g. a chunk of information from the ``note_1.txt`` file
created immediately above) can be imported by e.g.

    ./nb add --mode plain < note_1.txt

This, combined with the export mechanism, provides an easy way to email notes
to colleagues, so they can import them into their own databases.

Bug: this only works for *single* notes, at the present time.

### Dump database

Advanced users may want to dump the whole database with

    echo ".dump" | sqlite3 nb.db

### Back up the database

It is a good idea to set up a crontab entry like the following, to back up the
database daily (adjust the filenames appropriately).

    @daily echo ".dump" | sqlite3 /Users/kelley/Dropbox/nb.db | gzip -c > /Users/kelley/backup/nb/nb-`date +\%Y-\%m-\%d-\%H\%M`.gz

(This could be done better by checking the sha value of the file, to only
backup when things have changed.)

### Task count in bash prompt

To get a list of notes that are due today, put the following in your ``~/.bash_profile`` file:

    function nb_count {
        nb find --due today --count
    }
    PS1="\h:\W"
    export PS1="$PS1<\$(nb_count)> "



## Discussion items

The author would like advice on any bugs that users find, or any features that
they might like to see.  Almost any advice is likely to be helpful.  To get the
ball rolling, below is a list of topics that are likely to come up:

* There should be a graphical interface.  This is a lot of work, and will not
  be of too much use to power users, so it will come only after the general
functionality is settled.  Also, it will likely be web-based because then it
will work on all platforms.

* There should be an interface to a text editor, both for adding items and
  editing them.  (Suggestion of @richardsc)

* ... your item here :-)
