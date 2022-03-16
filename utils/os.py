# -*- coding: utf-8 -*-
# File: os.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2021/12/9 17:12
import os

from . import ospath as path
from .aio_wrap import aio_wrap

makedirs = aio_wrap(os.makedirs)
listdir = aio_wrap(os.listdir)
getcwd = aio_wrap(os.getcwd)

__all__ = [
    'path',
    'makedirs',
    'listdir',
    'getcwd',
]
