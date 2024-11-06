import threading
from typing import TypeVar, Generic, Callable, Any


T = TypeVar("T")


class ThreadWithResult(threading.Thread, Generic[T]):
    # "https://stackoverflow.com/a/65447493/17881894"
    """
    custom threading that also return a result value. just call `thread.result` after `thread.join()`.
    to get result of target thread actually you can just make a caller func as thread target
    and store main func in global variable (with 'global' keyword) to change previous variable. example:
    >>> result = None
    >>> def caller(arg1):
    >>>     global result # important
    >>>     result = functionToCall(arg1)
    >>> thread = threading.Thread(target=caller, args("test",))
    >>> thread.start()
    >>> thread.join() # wait thread ended before next line
    >>> print(result)
    """
    result: T = None

    def __init__(
        self,
        group=None,
        target: Callable[..., T] = None,
        name=None,
        args=(),
        kwargs={},
        *,
        daemon=None
    ):
        def function():
            self.result = target(*args, **kwargs)

        super().__init__(group=group, target=function, name=name, daemon=daemon)
