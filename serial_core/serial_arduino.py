# -*- coding: utf-8 -*-
# File: serial_arduino.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2022/3/16 14:07
import logging
import time

import serial
import serial.tools.list_ports_windows as s_tools

from utils import d_utf8, utf8

# 日志器
logger = logging.getLogger()


class SerialArduino(object):
    """
    上位机与arduino通信类
    """
    # arduino 所在串口
    com = None
    # 串口通信对象
    serial = None
    # 验证arduino串口的校验值 默认为 “..”
    check_key = None
    # 单个串口校验的有效时间 默认为 2 秒
    check_timeout = None

    def __init__(self, check_key="..", check_time=2, com=None):
        self.check_key = check_key
        self.check_time = check_time
        if com:
            self.com = com
        else:
            self.get_arduino_port()

    def __del__(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def get_arduino_port(self) -> None:
        """
        获取可用连接的串口
        :return comports: 串口字典
        """
        logger.info("No default port set,start get arduino connected port")
        iterator = sorted(s_tools.comports())
        for _, (port, desc, _) in enumerate(iterator, 1):
            try:
                serial_obj = serial.Serial(port, 9600, timeout=1)
            except Exception as e:
                # 捕获到异常说明这个串口已经被使用，直接跳过
                continue
            else:
                if self.check_comports(serial_obj):
                    logger.info(f"Arduino connected in port {port}!")
                    break
                else:
                    logger.warning("No such port connected to arduino!")

    def check_comports(self, serial_obj) -> bool:
        """
        检测arduino是否在此串口
        :param serial_obj:  串口对象
        """
        self.send_msg(".", serial_obj)
        n = 0
        while n < self.check_time:
            res = self.read_msg(serial_obj)
            if res == self.check_key:
                self.serial = serial_obj
                return True
            time.sleep(1)
            n += 1
        return False

    def send_msg(self, msg: str, serial_obj=None) -> None:
        """
        通过串口发送消息
        :param msg: 信息
        :param serial_obj: 串口对象 如果没有默认使用类里的串口对象
        """
        if serial_obj and serial_obj.is_open:
            serial_obj.write(utf8(msg))
        elif self.serial and self.serial.is_open:
            self.serial.write(utf8(msg))

    def read_msg(self, serial_obj=None):
        """
        获取串口消息
        :param serial_obj: 串口对象 如果没有默认使用类里的串口对象
        :return: 串口返回消息
        """
        if serial_obj and serial_obj.is_open:
            return d_utf8(serial_obj.read())
        elif self.serial and self.serial.is_open:
            return d_utf8(self.serial.read())


if __name__ == '__main__':
    serial_arduino = SerialArduino()
