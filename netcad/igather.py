# The `igather` async generator was found here:
#   https://bugs.python.org/issue30782
#   Author: Andrey Paramonov (aparamon)
#
# in a discussion on how to treat a large collection of tasks.  I've modified the code
# slightly so that I get back the original coroutine; but beyond that it is as it was found.


import asyncio


DEFAULT_MAX_TASKS = 100


__all__ = ["as_completed", "igather"]


async def as_completed(coros, limit=None):
    coros = iter(coros)

    buf = asyncio.Queue()
    sem = asyncio.Semaphore(limit or DEFAULT_MAX_TASKS)

    async def submit(_coros, _buf):
        while True:
            await sem.acquire()
            try:
                # TODO: additionally support async iterators
                _coro = next(_coros)
            except StopIteration:
                break
            _task = asyncio.create_task(_coro)
            _buf.put_nowait(_task)
        await _buf.put(None)

    async def consume(_buf):
        while True:
            _task = await _buf.get()
            if _task:
                v = await asyncio.wait_for(_task, None)
                sem.release()
                yield _task.get_coro(), v  # the yield will be Tuple(original-coro, task-result)
            else:
                break

    submit_task = asyncio.create_task(submit(coros, buf))

    try:
        async for result in consume(buf):
            yield result

    except Exception as exc:  # noqa
        submit_task.cancel()
        # cancel scheduled
        while not buf.empty():
            task = buf.get_nowait()
            if task:
                task.cancel()
                try:
                    await task
                except Exception:
                    pass

        # cancel pending
        for coro in coros:
            asyncio.create_task(coro).cancel()

        raise exc


async def igather(coros, limit=None):
    async for _ in as_completed(coros, limit or DEFAULT_MAX_TASKS):
        pass
