BEGIN TRANSACTION;
    CREATE TABLE note(noteId integer primary key autoincrement,
        authorId,
        date,
        title,
        content,
        privacy DEFAULT 0,
        views DEFAULT 0);
    CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);
    CREATE TABLE aliase(aliasId integer primary key autoincrement, item, alias);
    CREATE TABLE keyword(keywordId integer primary key autoincrement, keyword);
    CREATE TABLE notekeyword(notekeywordId integer primary key autoincrement, noteid, keywordid);
    INSERT INTO author(name, nickname) VALUES ("Dan Kelley", "dk");
    INSERT INTO keyword(keyword) VALUES ("lecture");
    INSERT INTO keyword(keyword) VALUES ("R");
    INSERT INTO note (authorId, date, title, content) VALUES (1, date('now'), 'John Cook lecture on R', 'http://channel9.msdn.com/Events/Lang-NEXT/Lang-NEXT-2012/Why-and-How-People-Use-R');
    INSERT INTO notekeyword(noteid, keywordid) VALUES (1, 1);
    INSERT INTO notekeyword(noteid, keywordid) VALUES (1, 2);
    INSERT INTO keyword(keyword) VALUES ("physics");
    INSERT INTO note (authorId, date, title, content, views) VALUES (1, date('now'), 'MIT physics lectures by Water Lewin', 'http://ocw.mit.edu/courses/physics/8-01-physics-i-classical-mechanics-fall-1999/index.htm', 0);
    INSERT INTO notekeyword(noteid, keywordid) VALUES (2, 1);
    INSERT INTO notekeyword(noteid, keywordid) VALUES (2, 3);
    INSERT INTO keyword(keyword) VALUES ("note aggregator");
    INSERT INTO note (authorId, date, title, content) VALUES (1, date('now'), 'need feedback on database categories', 'Asked DB, DI and CR.');
    INSERT INTO notekeyword(noteid, keywordid) VALUES (3, 4);
    INSERT INTO note (authorID, date, title, content) VALUES (1, date('now'), 'Q on SQL', 'http://stackoverflow.com/questions/14836568/sql-join-with-boolean-on-where');
    INSERT INTO keyword(keyword) VALUES ('SQL');
    INSERT INTO notekeyword(noteid, keywordid) VALUES (4, 5);
    COMMIT;

