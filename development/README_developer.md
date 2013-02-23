# Developer notes, ideas, questions, tasks, ...

1. If

    na --action add

(with no other args) enter interactive mode, quering for title etc.

2. Should process a dotfile.  Q: does python have a good way to do that, and
suggestions for format, e.g. as in django?

## Ideas for database storage

NB. on apple devices, the cloud is at e.g. (for Preview) ``~/Library/Mobile\
Documents/com~apple~Preview/Documents`` but it's not clear whether special
actions must be undertaken to set up a subdirectory in this area.  Possibly
[this appleinsideer
essay](http://appleinsider.com/articles/11/11/02/hidden_drop_box_feature_in_mac_os_x_lion_lets_you_sync_files_across_macs)
will say more.  At least in the first instance, Dropbox seems preferable, but
in any case the application needs a configuration scheme to permit selection of
the location of the database file.


## Timetable

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


