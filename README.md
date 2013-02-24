# 'nb', an open-source note-taking CLI/web/gui application

## Overview

It is easy to record brief notes for use in the short term, e.g. by writing a
line in a file named "README".  Others might call the file "notes" or,
depending on the content, "plans" or "ideas", "problems", etc.  As notes
accumulate, however, it can grow increasingly difficult to decide in which file
to put a new note.  Does an idea for fixing a problem belong in "ideas" or
"problems"?  One solution to this is to use a single file that merges notes of
a variety of types, with a categorization scheme to organize the material.
That scheme might involve titles and keywords that the author has associated
with notes, the time of note creation, etc.

For small tasks, a simple text file can work quite well, but this approach
grows cumbersome as notes accumulate, both for adding notes and for finding
them.  Using a general-purpose editor is risky because the process of adding a
new note can result in the destruction of existing notes.  Sifting through
notes with a general editor is also problematic, unless strict formatting
procedures are followed.

Using a database to store notes solves these problems.  Databases are ideal for
binding notes together with keywords, etc., and the isolation they provide
between the data and the user is helpful in preventing accidental deletion of
notes.

The ``nb`` application (named for the Latin phrase "nota bene") is designed
with these things in mind.  It provides several ways to add notes, and to
search through existing notes.  So far, it functions entirely at the unix
command line, and is most suited for power users who are unafraid of that
environment.

The development model for ``nb`` is entirely open-source.  It stores notes in a
database in the [sqlite](http://www.sqlite.org/) format, and is coded in the
[python](http://python.org) programming language; both of these are open-source
products that are freely available on most computing platforms.  The
open-source nature of ``nb`` is important because it saves the problem that
arises when users grow dependent on a software tool that may cease to work if 
a company goes out of business.

## Timeline

### 2013-02

* Develop a series of trial versions that will be suitable for use by the
  author in his own work.

* Tell others of the project and invite discussion of features (especially
  database design).

### 2013-03

* Based on experience in everyday use, firm up the database design.

* Invite other developers to work on editor-based versions.

* Develop a trial web-based version.


### Using nb

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


#### Add notes

This may be done one at a time, with commandline arguments, e.g.

    ./nb add --keywords 'lecture,physics,MIT' --title="Walter Lewin physics lectures" --content="http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm"

or via prompted interaction,

    ./nb add

One or more notes can also be added through input of a JSON file, e.g.

    ./nb add --format json --file note.json

#### Find notes

At present, the only way to find notes is by searching for a keyword, e.g.

    ./nb find --keyword "lecture"

To get all the notes, use

    ./nb find

#### Export notes

Notes may be exported to a JSON file by e.g.

    ./nb find --format json > notes.json

#### Dump database

Advanced users may want to dump the whole database with

    echo ".dump" | sqlite3 nb.db

#### Back up the database

It is a good idea to set up a crontab entry like the following, to back up the
database daily (adjust the filenames appropriately).

    @daily echo ".dump" | sqlite3 /Users/kelley/Dropbox/nb.db | gzip -c > /Users/kelley/backup/nb/nb-`date +\%Y-\%m-\%d-\%H\%M`.gz

(This could be done better by checking the sha value of the file, to only
backup when things have changed.)

