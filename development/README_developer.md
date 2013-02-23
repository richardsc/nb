# Developer discussion

## json i/o tests

Having problems with some existing items, using json output then input.

Below is a test that shows that this should be possible. 

    >>> import json
    >>> json.loads(json.dumps({"a":1, "b":"hello\nth\"ere\'buddy"}))
    {u'a': 1, u'b': u'hello\nth"ere\'buddy'}


