import pytest
from pprint import pprint as pp
import workflow as workflow
from unittest.mock import patch

class TestWorkflow1():
    def test1(self):
        w = workflow.Workflow1()
        store = dict(target=1)
        w.start(store=store)
        w >> Task1() >> Task2()
        if store['status']:
            w >> Task3a()
        else:
            w >> Task3b()
        for file in store['files']:
            w >> Task4(file=file)
        
        w.end()


class TestDiff:
    def test_1(self):
        store = dict(
            files=['1.csv'],
        )
        diff = workflow.Diff()
        actual = diff.run(store)
        assert actual == True
        assert store['diff'] == [
            dict(
                diff_exists=True,
                file='1.csv',
                stdout="stdouts\nstdouts",
                stderr="stderr\nstderr"
            ),
        ]

class TestIfCheckModeThenShowSummaryAndBreak():
    @pytest.fixture(scope='function', autouse=False)
    def store(self):
        store = dict(
            diff=[
                dict(
                    diff_exists=True,
                    file='1.csv',
                    stdout="stdouts\nstdouts",
                    stderr="stderr\nstderr"
                ),
            ],
        )
        yield store

    def test1(self, store):
        task = workflow.IfCheckModeThenShowSummaryAndBreak(checkmode=True)
        actual = task.run(store)
        assert actual == False

    def test2(self, store):
        task = workflow.IfCheckModeThenShowSummaryAndBreak(checkmode=False)
        actual = task.run(store)
        assert actual == True

class TestCheckState():
    @pytest.fixture(scope='function', autouse=False)
    def store(self):
        store = dict(
            files=['1.csv'],
        )
        yield store

    @pytest.fixture(scope='function', autouse=True)
    def state_is(self, request):
        state = request.param
        with patch('workflow.CheckState.get_state') as m:
            m.return_value = dict(
                enable=True,
                disable=False)[state]
            yield

    decision_table = [
        ('enable', 'enable', True),
        ('enable', 'disable', False),
        ('disable', 'enable', False),
        ('disable', 'disable', True),
        
    ]
    @pytest.mark.parametrize('state_is, eq, expected', decision_table, indirect=['state_is'])
    def test1(self, store, eq, expected):
        task = workflow.CheckState(eq=eq)
        actual = task.run(store)
        assert actual == expected

class TestSetState():
    @pytest.fixture(scope='function', autouse=True)
    def set_state_to(self):
        with patch('workflow.SetState.set_state_to') as m:
            m.return_value = True
            yield

    @pytest.fixture(scope='function', autouse=False)
    def store(self):
        store = dict(
            files=['1.csv'],
        )
        yield store

    def test(self, store):
        task = workflow.SetState(to='enable')
        actual = task.run(store)
        assert actual == True
