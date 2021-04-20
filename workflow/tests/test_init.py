import pytest
from pprint import pprint as pp
import workflow as workflow

class TestDiff:
    def test_1(self):
        store = dict(
            files=['1.csv'],
        )
        diff = workflow.Diff()
        diff.run(store)
        assert store['diff'] == [
            dict(
                diff_exists=True,
                file='1.csv',
                stdout="stdouts\nstdouts",
                stderr="stderr\nstderr"
            ),
        ]


