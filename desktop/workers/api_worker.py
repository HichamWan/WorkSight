from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

_alive = set()   # keeps tasks alive until they finish


class _Signals(QObject):
    done = Signal(object)
    failed = Signal(str)


class _Task(QRunnable):
    def __init__(self, fn, args, kwargs):
        super().__init__()
        self.setAutoDelete(False)
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.signals = _Signals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.failed.emit(str(e))
        else:
            self.signals.done.emit(result)


def run_async(fn, on_done, on_fail=None, *args, **kwargs):
    """Run fn(*args) in the background, then call on_done(result) on the UI thread."""
    task = _Task(fn, args, kwargs)
    _alive.add(task)

    def finish(callback):
        def wrapper(value):
            _alive.discard(task)
            if callback:
                callback(value)
        return wrapper

    task.signals.done.connect(finish(on_done))
    task.signals.failed.connect(finish(on_fail))
    QThreadPool.globalInstance().start(task)