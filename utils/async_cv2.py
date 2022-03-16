# -*- coding: utf-8 -*-
# File: async_cv2.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2021/12/9 17:39
import cv2

from .aio_wrap import aio_wrap

imread = aio_wrap(cv2.imread)