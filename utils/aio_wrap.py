# -*- coding: utf-8 -*-
# File: aio_wrap.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2021/12/9 17:29
import asyncio
from functools import partial, wraps

loop = asyncio.get_event_loop()


def aio_wrap(func):
    @wraps(func)
    async def run(*args, executor=None, **kwargs):
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run
