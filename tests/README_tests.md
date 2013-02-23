hese notes will probably not be useful to anyone but the developer.  Mostly,
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



