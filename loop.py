""" Implements event-loop class. """

class Loop:
    def __init__(self, poll, tasks):
        self.poll = poll
        self.tasks = tasks
        self.index = {}

    def accept(self, sock, action):
        # Accept task for socket-action.
        task = self.index.get((sock, action))
        if task is None:
            return None

        # Clean listeners and state.
        self.poll.unwatch(sock, action)
        del self.index[sock, action]

        return task

    def step(self, task):
        try:
            # Continue coroutine.
            sock, action = task.send(None)
        except StopIteration as e:
            # Coroutine is finished.
            return task, True, e.value
        else:
            # Plan execution for future.
            self.poll.watch(sock, action)
            self.index[sock, action] = task

            # Coroutine is not finished.
            return task, False, None

    def run(self):
        pending = set(self.tasks)
        results = {}

        # Init coroutines.
        for task in self.tasks:
            self.step(task)

        # Handle events.
        for sock, action in self.poll.events():
            task = self.accept(sock, action)
            if not task:
                continue

            reaction = self.step(task)
            if not reaction:
                continue

            task, ready, result = reaction
            if not ready:
                continue

            pending.remove(task)
            results[task] = result
            if not pending:
                return results
