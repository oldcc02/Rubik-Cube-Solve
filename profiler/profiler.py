# -*- coding: utf-8 -*-
# File: profiler.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/10/15 14:25
from pyinstrument import Profiler


def aio_profiler(function):
    """
    异步函数性能测试装饰器
    """
    profiler_async = Profiler(async_mode='enabled')

    async def inner(*args, **kwargs):
        profiler_async.start()
        await function(*args, **kwargs)
        profiler_async.stop()
        profiler_async.print()

    return inner


def syn_profiler(function):
    """
    同步函数装饰器
    """
    profiler = Profiler()

    def inner():
        profiler.start()
        function()
        profiler.stop()
        profiler.print()

    return inner
