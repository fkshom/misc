
class Workflow:
    def __init__(self):
        self.tasks = []

    def run(self):
        pass

    def __lshift__(self, other):
        self.tasks.append(other)
        return self

class Task:
    pass

class CheckState(Task):
    def __init__(self, eq):
        self.state = eq

    def run(self, w):
        w.datastore
        w.result = True
        return True


def main():
    w = Workflow()

    w << Diff()

    if mode == 'enable':
        w << (
            CheckState(eq='enable'),
            SetState(to='disable'),
            CheckState(eq='disable'),
        )
    elif mode == 'disable':
        w << (
            CheckState(eq='disable'),
        )
    elif mode == 'force-enable':
        w << (
            SetState(to='disable'),
            CheckState(eq='disable'),
        )
    elif mode == 'force-disable':
        w << (
            SetState(to='disable'),
            CheckState(eq='disable'),
        )
    else:
        raise Exception()

    w << (
        Replace(),
        Diff()
    )

    if mode == 'enable':
        w << (
            CheckState(eq='disable'),
            SetState(to='enable'),
            CheckState(eq='enable'),
        )
    elif mode == 'disable':
        w << (
            CheckState(eq='disable'),
        )
    elif mode == 'force-enable':
        w << (
            SetState(to='enable'),
            CheckState(eq='enable'),
        )
    elif mode == 'force-disable':
        w << (
            SetState(to='disable'),
            CheckState(eq='disable'),
        )
    else:
        raise Exception()

    datastore = {}
    w.run(datastore)

if __name__ == '__main__':
    main()
