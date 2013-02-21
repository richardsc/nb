# 'na', an open-source note-taking CLI/web/gui application

## Overview

Most of us take notes on lots of things through the day, and would like a way
to store them for a long time, and access them easily hours or years later, by
searching content, looking in date ranges, sifting through keywords, etc.  Once
there are more than a few notes, it will become important to be able to edit
them, comment upon them, make links between them, etc.  Notes should be
accessible from a variety of devices, which calls for a cloud-like storage
mechanism.



## Features

1. ubiquitous

2. keywords 

3. update history (not implemented yet)

4. text + graphs (graphs not implemented yet)

5. interaction from commandline (initially), with a python module that will
   make for easy extension to emacs/vim interaction, web interaction, and gui
interaction.

6. open-source, meaning zero cost and no worries about company bankrupcy



## Development notes

### Ideas for database storage

NB. on apple devices, the cloud is at e.g. (for Preview) ``~/Library/Mobile\
Documents/com~apple~Preview/Documents`` but it's not clear whether special
actions must be undertaken to set up a subdirectory in this area.  Possibly
[this appleinsideer
essay](http://appleinsider.com/articles/11/11/02/hidden_drop_box_feature_in_mac_os_x_lion_lets_you_sync_files_across_macs)
will say more.  At least in the first instance, Dropbox seems preferable, but
in any case the application needs a configuration scheme to permit selection of
the location of the database file.


### Timetable

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


### Suggestions for collaborators

#### Create database

    make


#### Test database

    make test

#### Add a note

    ./na --action add --title "oceanpython lecture" --keyword "lecture,python" --content "Diego gave a great talk"

#### Find a note by keyword

    ./na --action find --keyword "lecture"

#### Dump database

    echo ".dump" | sqlite3 na.db



