import asyncio
from asyncio import futures
from asyncio.tasks import CoroWrapper
import functools
import inspect


def coroutine(func):
    """Decorator to mark coroutines.

    If the coroutine is not yielded from before it is destroyed,
    an error message is logged.
    """
    if inspect.isgeneratorfunction(func):
        coro = func
    else:
        @functools.wraps(func)
        def coro(*args, **kw):
            res = func(*args, **kw)
            if isinstance(res, futures.Future) or inspect.isgenerator(res):
                res = yield from res
            return res

    if False:  # not _DEBUG:
        wrapper = coro
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            w = CoroWrapper(coro(*args, **kwds), func)
            w.__name__ = coro.__name__
            w.__doc__ = coro.__doc__
            return w

    wrapper._is_coroutine = True  # For iscoroutinefunction().
    return wrapper

@coroutine
def slow_operation():
    yield from asyncio.sleep(1)
    return "Complete"


def got_result(future):
    print(future.result())
    loop.stop()

loop = asyncio.get_event_loop()

try:
    reply = loop.run_until_complete(slow_operation())
    print(reply)
finally:
    loop.close()