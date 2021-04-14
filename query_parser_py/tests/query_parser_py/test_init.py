import pytest
import query_parser_py
from pprint import pprint as pp

@pytest.fixture(scope='function', autouse=False)
def data():
    return ([
        dict(title="foo", body="unko0"),
        dict(title="fox", body="unko1"),
        dict(title="cat", body="unko2"),
        dict(title="dog", body="unko3"),
        dict(title="bar bar", body="unko4"),
    ])

datas = [
    ("title:fox", 
     [dict(title='fox', body="unko1")]
    ),
    ("title:fox OR title:dog OR title:cat",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3")]
    ),
    ("title:fox AND body:unko1",
     [dict(title="fox", body="unko1")]
    ),
    ("title:fox AND body:unko1 OR title:cat",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2")]
    ),
    ("(title:fox AND body:unko1) OR title:cat",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2")]
    ),
    ("title:(fox OR cat)",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2")]
    ),
    ("title:/fox|cat/",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2")]
    ),
    ("title:/f.x|c.*t/",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2")]
    ),
    ("title:(/f.*/ AND /.o./)",
     [dict(title="foo", body="unko0"),
      dict(title="fox", body="unko1")]
    ),
    ("title:fox OR body:unko2",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2")]
    ),
    ("title:f*",
     [dict(title="foo", body="unko0"),
      dict(title="fox", body="unko1")]
    ),
    ('title:"bar bar"',
     [dict(title="bar bar", body="unko4")]
    ),
    ('dummy:abc',
     []
    ),
    ('dummy:/abc/',
     []
    ),
    ('dummy:abc*',
     []
    ),
    ('dummy:"abc def"',
     []
    ),
    ('NOT title:fox',
     [dict(title="foo", body="unko0"),
      dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3"),
      dict(title="bar bar", body="unko4")]
    ),
    ('NOT title:fox AND NOT title:foo',
     [dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3"),
      dict(title="bar bar", body="unko4")]
    ),
    ('NOT title:fox OR NOT title:foo',
     [dict(title="foo", body="unko0"),
      dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3"),
      dict(title="bar bar", body="unko4")]
    ),
    ('NOT (title:fox AND title:foo)',
     [dict(title="foo", body="unko0"),
      dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3"),
      dict(title="bar bar", body="unko4")]
    ),
    ('NOT (title:fox OR title:foo)',
     [dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3"),
      dict(title="bar bar", body="unko4")]
    ),
    ('NOT NOT title:fox',
     [dict(title="fox", body="unko1"),]
    ),
    ('NOT NOT NOT title:fox',
     [dict(title="foo", body="unko0"),
      dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3"),
      dict(title="bar bar", body="unko4")]
    ),
]

@pytest.mark.parametrize("query, expected", datas)
def test(data, query, expected):
    matcher = query_parser_py.MatcherBase(query)
    result = []
    for row in data:
        if matcher.is_matched(row):
            result.append(row)
    pp(result)
    assert result == expected


datas1 = [
    ("title:fox", 
     [dict(title='fox', body="unko1")]
    ),
    ("title:(fox cat dog)",
     [dict(title="fox", body="unko1"),
      dict(title="cat", body="unko2"),
      dict(title="dog", body="unko3")]
    ),
    ("title:fox body:unko1",
     [dict(title="fox", body="unko1")]
    ),
]

@pytest.mark.parametrize("query, expected", datas1)
def test(data, query, expected):
    matcher = query_parser_py.Matcher(query)
    result = []
    for row in data:
        if matcher.is_matched(row):
            result.append(row)
    pp(result)
    assert result == expected

