# -*- coding: utf-8 -*-
# File: serial_arduino.py
# @Author: 黄文俊

# @Time: 2022/3/16 14:07
import sys
import time

import serial as s
import serial.tools.list_ports_windows as s_tools

from utils import d_utf8, utf8, new_logger

# 日志器
logger = new_logger(__file__)


class SerialArduino(object):
    """
    上位机与arduino通信类
    """
    # arduino 所在串口
    com = None
    # 串口通信对象
    serial = None
    # 验证arduino串口的校验值 默认为 “z”，
    # 修改此处需要对应修改arduino收到此消息做出的响应 即 CHECK_KEY
    CALL_KEY = "z"
    # arduino验证时返回的校验值 默认为 “o”
    CHECK_KEY = "o"
    # 单个串口校验的有效时间 默认为 2 秒
    CHECK_TIMEOUT = 1
    # 在通过串口与arduino新建立连接时会导致arduino重启 ，这个时间是等待重启的时间
    # 如果不设置此时间会导致消息无法发送到arduino
    WAIT_TIMEOUT = 4

    def __init__(self, com=None, **kwargs):
        for k, v in kwargs:
            setattr(self, k, v)
        if com:
            self.com = com
            self.check_comports()
        else:
            self.get_arduino_port()

    def __del__(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def get_arduino_port(self) -> None:
        """
        获取Arduino所在串口
        """
        logger.info("No default port set!")
        logger.info("Start scan ports to find which port running arduino")
        iterator = sorted(s_tools.comports())
        for _, (port, desc, _) in enumerate(iterator, 1):
            try:
                serial_obj = self.new_serial_obj(port)
            except Exception as e:
                # 捕获到异常说明这个串口已经被使用，直接跳过
                continue
            else:
                if self.check_comports(serial_obj):
                    break
        if not self.serial:
            logger.warning("No such port connected to arduino!")

    def new_serial_obj(self, port: str) -> s.Serial:
        """
        新建serial对象
        :param port: 串口号
        :return 串口对象
        """
        try:
            serial = s.Serial(port, 9600, timeout=self.CHECK_TIMEOUT)
        except Exception as e:
            raise e
        time.sleep(self.WAIT_TIMEOUT)
        return serial

    def check_comports(self, serial_obj: s.Serial = None) -> bool:
        """
        检测arduino是否在此串口
        :param serial_obj:  串口对象
        """
        try:
            if self.com:
                serial_obj = self.new_serial_obj(self.com)
            while serial_obj.read():
                continue
            self.send_msg(self.CALL_KEY, serial_obj)
            n = 0
            while n < self.CHECK_TIMEOUT:
                res = self.read_msg(serial_obj)
                if res == self.CHECK_KEY:
                    self.serial = serial_obj
                    logger.info(f"Arduino connected in port {serial_obj.name}!")
                    return True
                time.sleep(1)
                n += 1
            return False
        except Exception as e:
            logger.info("check comport failed error: {}".format(e))
            return False

    def send_msg(self, msg: str, serial_obj: s.Serial = None) -> None:
        """
        通过串口发送消息
        :param msg: 信息
        :param serial_obj: 串口对象 如果没有默认使用类里的串口对象
        """
        logger.info(f"send {msg} to {self.serial.name if self.serial else serial_obj.name}")
        if serial_obj and serial_obj.is_open:
            serial_obj.write(utf8(msg))
        elif self.serial and self.serial.is_open:
            self.serial.write(utf8(msg))

    def read_msg(self, serial_obj: s.Serial = None):
        """
        获取串口消息
        :param serial_obj: 串口对象 如果没有默认使用类里的串口对象
        :return: 串口返回消息
        """
        res = None
        i = 0
        while i < 5 and (res is None or res == ""):
            if serial_obj and serial_obj.is_open:
                res = d_utf8(serial_obj.read())
            elif self.serial and self.serial.is_open:
                res = d_utf8(self.serial.read())
            if res:
                break
            i += 1
            time.sleep(1)
        logger.info(f"receive {res} from {self.serial.name if self.serial else serial_obj.name}")
        return res

    def check_cube(self):
        self.send_msg("n")
        self.shake_hand()
        self.send_msg("o")
        self.shake_hand()
        self.send_msg("p")
        self.shake_hand()
        self.send_msg("q")
        self.shake_hand()
        self.send_msg("r")
        self.shake_hand()
        self.send_msg("s")
        self.shake_hand()

    def shake_hand(self):
        i = 0
        while i < 2:
            if self.read_msg() == self.CHECK_KEY:
                time.sleep(1)
                self.send_msg(self.CALL_KEY)
                return
            i += 1
        logger.error("shake_hand failed timeout")
        sys.exit(1)


if __name__ == '__main__':
    serial_arduino = SerialArduino("COM4")
    # serial_arduino.send_msg("c")
    serial_arduino.check_cube()
    # serial_arduino.send_msg("0")
    # serial_arduino.send_msg("7")
    # serial_arduino.send_msg("8")
