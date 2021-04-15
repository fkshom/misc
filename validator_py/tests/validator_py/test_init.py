import pytest
import validator_py

class Test1:
    def test_1(self):
        rulestore = validator_py.RuleStore()
        rulestore.load_from_string()
        rulestore.validate()

        assert len(rulestore.errors) == 2

