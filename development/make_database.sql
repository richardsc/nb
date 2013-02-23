BEGIN TRANSACTION;
    CREATE TABLE note(noteId integer primary key autoincrement,
        authorId,
        date,
        title,
        content,
        privacy DEFAULT 0,
        views DEFAULT 0);
    CREATE TABLE author(authorId integer primary key autoincrement, name, nickname);
    CREATE TABLE alias(aliasId integer primary key autoincrement, item, alias);
    CREATE TABLE keyword(keywordId integer primary key autoincrement, keyword);
    CREATE TABLE notekeyword(notekeywordId integer primary key autoincrement, noteid, keywordid);
    COMMIT;

