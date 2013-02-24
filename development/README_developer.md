# Developer discussion

## db columns

* what is the point of 'views' in 'note'?

* what is the point of the 'author' table?

* maybe 'note' should have an item for priority

* maybe 'note' should have timing items e.g. 'doBefore' or 'status', for planning

## json i/o tests

Having problems with some existing items, using json output then input.

Below is a test that shows that this should be possible. 

    >>> import json
    >>> json.loads(json.dumps({"a":1, "b":"hello\nth\"ere\'buddy"}))
    {u'a': 1, u'b': u'hello\nth"ere\'buddy'}

## removing unused keywords

Need to use 'count'.

Some trials below (just for cut/paste):

select keywordId, (select count(notekeyword.keywordid) from keyword JOIN notekeyword on notekeyword.keywordid = keyword.keywordid) from keyword;

select * from keyword JOIN notekeyword on notekeyword.keywordid = keyword.keywordid;


