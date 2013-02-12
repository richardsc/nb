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
    INSERT INTO note (authorID, date, title, content, views) VALUES (1, date('now'), 'Q on SQL', 'http://stackoverflow.com/questions/14836568/sql-join-with-boolean-on-where', 0);
    INSERT INTO tag(tag) VALUES ('SQL');
    INSERT INTO notetag(noteid, tagid) VALUES (4, 5);
    COMMIT;

