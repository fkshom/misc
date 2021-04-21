
class Workflow:
    def __init__(self):
        self.tasks = []

    def __lshift__(self, other):
        if type(other) == list:
            self.tasks.extend(other)
        else:
            self.tasks.append(other)
        return self

    def show(self):
        print(f"Show Workflow")
        for task in self.tasks:
            task.show()
        print()

    def run(self, store):
        for task in self.tasks:
            print(f"[DEBUG] Start {task.__class__.__name__}")
            result = task.run(store)
            store['returncode'] = 0
            if result:
                continue
            else:
                store['returncode'] = 1
                break

        return store

class Task:
    def __init__(self, **kwargs):
        self.params = kwargs

    def show(self):
        print(f"  {self.__class__.__name__}")

class Diff(Task):
    def run(self, store):
        for file in store['files']:
            print(f'diff {file}')
            store.setdefault('diff', [])
            store['diff'].append(dict(
                diff_exists=True,
                file=file,
                stdout="stdouts\nstdouts",
                stderr="stderr\nstderr",
            ))
        return True

class IfCheckModeThenShowSummaryAndBreak(Task):
    def run(self, store):
        if self.params['checkmode']:
            print("Sumamry")
            for diffresult in store['diff']:
                print()
                print(f"  file: {diffresult['file']}")
                print(f"  diff_exists: {diffresult['diff_exists']}")
            print("This is CHECK MODE")
            return False
        return True

class IfNoDifExistsThenBreak(Task):
    def run(self, store):
        if store['diff'][0]['diff_exists']:
            print(f"  diff exists")
            return True
        else:
            print(f"  NO diff exists")
            return False

class CheckState(Task):
    def run(self, store):
        current_state = self.get_state()
        desired_state = dict(enable=True, disable=False)[self.params['eq']]
        if current_state == desired_state:
            return True
        else:
            return False

    def get_state(self):
        vclient = self.engine.params['vclient']
        dvpg = DistributedVirtualPortgroup(vclient)
        dvpg.load('pg1')

        return True

class SetState(Task):
    def run(self, store):
        return True

    def set_state_to(self, to):
        return True

from rich.console import Console

def main():
    files = [
        'file/1.csv',
        'file/2.csv',
    ]

    mode = 'enable'
    print("START workflow_for_all")
    workflow_for_all = Workflow(vclient=vclient)

    workflow_for_all << Diff()
    workflow_for_all << IfCheckModeThenShowSummaryAndBreak(checkmode=False)
    datastore = dict(
        files=files
    )
    result = workflow_for_all.run(datastore)
    if result['returncode'] != 0:
        return

    print("START workflow")
    for file in files:
        w = Workflow()
        w << Diff() << IfNoDifExistsThenBreak()

        if mode == 'enable':
            w << [ CheckState(eq='enable'), SetState(to='disable'), CheckState(eq='disable'), ]
        elif mode == 'disable':
            w << ( CheckState(eq='disable'), )
        elif mode == 'force-enable':
            w << ( SetState(to='disable'), CheckState(eq='disable'), )
        elif mode == 'force-disable':
            w << ( SetState(to='disable'), CheckState(eq='disable'), )
        else:
            raise Exception()

        # w << (
        #     Replace(), Diff()
        # )

        # if mode == 'enable':
        #     w << ( CheckState(eq='disable'), SetState(to='enable'), CheckState(eq='enable'), )
        # elif mode == 'disable':
        #     w << ( CheckState(eq='disable'), )
        # elif mode == 'force-enable':
        #     w << ( SetState(to='enable'), CheckState(eq='enable'), )
        # elif mode == 'force-disable':
        #     w << ( SetState(to='disable'), CheckState(eq='disable'), )
        # else:
        #     raise Exception()

        datastore = dict(
            files=[file]
        )
        w.run(datastore)

if __name__ == '__main__':
    main()
