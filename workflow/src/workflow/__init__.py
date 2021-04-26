
class Workflow:
    def __init__(self):
        self.tasks = []
        self.state = 'init'
        self.task_history = []

    def __rshift__(self, other):
        return self.__lshift__(other)

    def __lshift__(self, other):
        tasks = []
        if type(other) == list:
            tasks.extend(other)
        else:
            tasks.append(other)
        
        self.task_history.extend(tasks)

        if self.state == 'failed':
            return self

        while tasks:
            task = tasks.pop(0)
            self.state = 'running'
            print(f"[DEBUG] Start {task.__class__.__name__}")
            result = task.run(self.store)
            if result:
                continue
            else:
                self.state = 'failed'
                break

        self.state = 'success'
        return self

    def show(self):
        print(f"Show Workflow")
        for task in self.tasks:
            task.show()
        print()

    def start(self, store):
        self.store = store

    def end(self):
        return self.state

class Task:
    def __init__(self, **kwargs):
        self.params = kwargs

    def show(self):
        print(f"  {self.__class__.__name__}")

    def run(self, store):
        print(f"[DEBUG] Start {self.__class__.__name__}")
        return True


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

class IfNoDiffExistsThenBreak(Task):
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

class VClient:
    def __init__(self):
        pass
    def content(self):
        return None

from rich.console import Console

def main():
    files = [
        ('file/1.csv', 'enable'),
        ('file/2.csv', 'disable'),
    ]

    print("START workflow_for_all")
    store = dict(
        files=files
    )
    vclient = VClient()
    vclient.connect(host='vcenter', user='user', password='pass', reuse=True)
    w = Workflow(vclient=vclient)
    w.start(store)
    w << Diff()
    w << IfCheckModeThenShowSummaryAndBreak(checkmode=False)
    result = w.end()

    if result == 'failed':
        return

    w = Workflow(vclient=vclient)
    for file, mode in store['files']:
        store = dict(
            file=file,
            mode=mode,
        )
        w.start(store)
        store['files'] = [file]
        w << Diff() << IfNoDiffExistsThenBreak()
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
        
        w << Replace() << Diff()

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

        result = w.end()
        if result == False:
            print(f"failed {file}")


if __name__ == '__main__':
    main()
