# -*- coding: utf-8 -*-
# File: msg_tools.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2022/3/16 17:50

def utf8(msg: str) -> bytes:
    return msg.encode("utf-8")


def d_utf8(msg: bytes) -> str:
    return msg.decode("utf-8")
