# -*- coding: utf-8 -*-
# File: ospath.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/9 17:25
import os

from .aio_wrap import aio_wrap

dirname = aio_wrap(os.path.dirname)
join = aio_wrap(os.path.join)
splitext = aio_wrap(os.path.splitext)
exists = aio_wrap(os.path.exists)

