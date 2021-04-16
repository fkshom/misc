import pytest
from assertpy import assert_that
from pprint import pprint as pp
from unittest.mock import patch
import validator_py
import io
import textwrap


class TestAlignedCsvLinter:
    @pytest.fixture(scope='function', autouse=False)
    def rulecsv1(self):
        csv = (
            "description , action , source_ip       , destination_ip  , source_port , destination_port , protocol , comment\n"
            "abcd        ,        ,192.168.11.1/32 , 192.168.12.1/32 , ANY         , ANY              , ANY      , cmt\n"
            "efgh        ,       , 192.168.11.1/32 , 192.168.12.1/32 , ANY         , ANY              , ANY      , \n"
        )
        yield csv

    def test_1(self, rulecsv1):
        rulecsvio = io.StringIO(rulecsv1)
        linter = validator_py.AlignedCsvLinter()
        linter.validate(rulecsvio)
        assert len(linter.errors) == 2

class TestRuleValidator:
    def test_1(self):
        v = validator_py.RuleValidator()
        v.validate({
            "description": "",
            "action": "accept",
            "source_ip": '1.1.1.1/24',
            "destination_ip": "2.2.2.2/24",
            "source_port": "32768-65535",
            "destination_port": "80",
            "protocol": "tcp",
        })
        assert v.errors == {}

    def test_1(self):
        v = validator_py.RuleValidator()
        v.validate({
            "description": "",
            "action": "test",
            "source_ip": '1.-1.1.1/24',
            "destination_ip": "2.2.2.2/33",
            "source_port": "32768a",
            "destination_port": "80udp",
            "protocol": "a",
        })
        assert v.errors == {
            'action': ['unallowed value test'],
            'source_ip': ["'source_ip' cant be parsed by ipaddr.IPv4Interface. 1.-1.1.1/24", "'source_ip' must be x.x.x.x/x or ANY. 1.-1.1.1/24"],
            'destination_ip': ["'destination_ip' cant be parsed by ipaddr.IPv4Interface. 2.2.2.2/33"],
            'source_port': ["value does not match regex '^\\d+$|^\\d+-\\d+$'"],
            'destination_port': ["value does not match regex '^\\d+$|^\\d+-\\d+$'"],
            'protocol': ['unallowed value a'],
        }


class TestRuleStore:
    @pytest.fixture(scope='function', autouse=False)
    def rulecsv1(self):
        rulecsv = textwrap.dedent("""
        dcname: dc01
        pgname: pg01
        ---
        description, action, source_ip, destination_ip, source_port, destination_port, protocol, comment
        abcdf, , 192.168.11.1/32, 192.168.12.1/32, ANY, ANY, ANY, cmt
        efgh, , 192.168.11.1/32, 192.168.12.1/32, ANY, ANY, ANY, 
        """)[1:-1]

        yield rulecsv

    @pytest.fixture(scope='function', autouse=False)
    def rulecsv2(self):
        rulecsv = textwrap.dedent("""
        dcname: dc01
        pgname: pg01
        ---
        description, action, source_ip, destination_ip, source_port, destination_port, protocol, comment
        abcdf, , 192.168.11.1/32, 192.168.12.1/32, ANY, ANY, ANY, cmt
        
        efgh, , 192.168.11.1/32, 192.168.12.1/32, ANY, ANY, ANY, 
        """)[1:-1]

        yield rulecsv

    def test_1(self, rulecsv1):
        rulecsvio = io.StringIO(rulecsv1)
        store = validator_py.RuleStore()
        store.load(rulecsvio)
        assert store.dcname == 'dc01'
        assert store.pgname == 'pg01'

        assert store.rules[0].to_dict() == dict(
            description='abcdf',
            source_ip='192.168.11.1/32',
            destination_ip='192.168.12.1/32',
            source_port='ANY',
            destination_port='ANY',
            protocol='ANY',
            action='',
            comment='cmt'
        )

        store.rules[0].description = 'abcd'

        rulecsvoutio = io.StringIO()
        store.save(rulecsvoutio, format=True)
        actual = rulecsvoutio.getvalue()
        expect = (
            "dcname: dc01\n"
            "pgname: pg01\n"
            "---\n"
            "description , action , source_ip       , destination_ip  , source_port , destination_port , protocol , comment\n"
            "abcd        ,        , 192.168.11.1/32 , 192.168.12.1/32 , ANY         , ANY              , ANY      , cmt\n"
            "efgh        ,        , 192.168.11.1/32 , 192.168.12.1/32 , ANY         , ANY              , ANY      , \n"
        )
        assert actual == expect

    def test_2(self, rulecsv2):
        rulecsvio = io.StringIO(rulecsv2)
        store = validator_py.RuleStore()
        store.load(rulecsvio)
        assert len(store.rules) == 2

        store.rules[0].description = 'abcd'

        rulecsvoutio = io.StringIO()
        store.save(rulecsvoutio, format=True)
        actual = rulecsvoutio.getvalue()
        expect = (
            "dcname: dc01\n"
            "pgname: pg01\n"
            "---\n"
            "description , action , source_ip       , destination_ip  , source_port , destination_port , protocol , comment\n"
            "abcd        ,        , 192.168.11.1/32 , 192.168.12.1/32 , ANY         , ANY              , ANY      , cmt\n"
            "efgh        ,        , 192.168.11.1/32 , 192.168.12.1/32 , ANY         , ANY              , ANY      , \n"
        )
        assert actual == expect

    def test_3(self):
        rulecsv = textwrap.dedent("""
        dcname: dc01
        pgname: pg01
        ---
        description, action, source_ip, destination_ip, source_port, destination_port, protocol, comment
        abcdf, ,,,,, 192.168.11.1/32, 192.168.12.1/32, ANY, ANY, ANY, cmt

        efgh, , 192.168.11.1/32, 192.168.12.1/32, ANY, ANY, ANY, 
        """)[1:-1]
        rulecsvio = io.StringIO(rulecsv)
        store = validator_py.RuleStore()
        store.load(rulecsvio)
        assert len(store.rules) == 2

        assert len(store.errors) == 1
        assert store.errors[0] == {'line_idx': 4, 'message': 'A number of columns is invalid. expect:8, actual:12. Anyway continue.'}
