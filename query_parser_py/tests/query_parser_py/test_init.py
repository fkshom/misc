import pytest
import query_parser_py
from pprint import pprint as pp

data = [
        dict(title="foo", body="unko0"),
        dict(title="fox", body="unko1"),
        dict(title="cat", body="unko2"),
        dict(title="dog", body="unko3"),
        dict(title="bar bar", body="unko4"),
]

def test_a1():
    query = "title:fox"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result == [dict(title='fox', body="unko1")]

def test_a2():
    query = "title:fox OR title:dog OR title:cat"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")
    assert result[2] == dict(title="dog", body="unko3")

def test_a3():
    query = "title:fox AND body:unko1"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")

def test_a4():
    query = "title:fox AND body:unko1 OR title:cat"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")

def test_a5():
    query = "(title:fox AND body:unko1) OR title:cat"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")

def test_a6():
    query = "title:(fox OR cat)"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")

def test_a7():
    query = "title:/fox|cat/"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")

def test_a8():
    query = "title:/f.x|c.*t/"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")

def test_a8():
    query = "title:(/f.*/ AND /.o./)"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="foo", body="unko0")
    assert result[1] == dict(title="fox", body="unko1")

def test_a9():
    query = "title:fox OR body:unko2"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="fox", body="unko1")
    assert result[1] == dict(title="cat", body="unko2")

def test_a10():
    query = "title:f*"
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="foo", body="unko0")
    assert result[1] == dict(title="fox", body="unko1")

def test_a11():
    query = 'title:"bar bar"'
    result = query_parser_py._main(data, query)
    pp(result)
    assert result[0] == dict(title="bar bar", body="unko4")