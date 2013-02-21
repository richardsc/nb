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



### Using na

#### Create database

    make

(Soon, this will be done with ``./na setup``)


#### Test database

    make test

#### Add a note

    ./na add --title "oceanpython lecture" --keyword "lecture,python,diego" --content "Diego now speaks twice per week"

#### Find a note by keyword

    ./na find --keyword "lecture"

#### Dump database

    ./na find
    echo ".dump" | sqlite3 na.db



