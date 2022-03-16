# -*- coding: utf-8 -*-
# File: serial_arduino.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2022/3/16 14:07
import time

import serial as s
import serial.tools.list_ports_windows as s_tools

from utils import d_utf8, utf8, new_logger

# 日志器
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s-%(levelname)s-%(name)s:  %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__file__)

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
    # 修改此处需要对应修改arduino收到此消息做出的响应 即 check_key
    call_key = "z"
    # arduino验证时返回的校验值 默认为 “o”
    check_key = "o"
    # 单个串口校验的有效时间 默认为 2 秒
    check_timeout = 1
    # 在通过串口与arduino新建立连接时会导致arduino重启 ，这个时间是等待重启的时间
    # 如果不设置此时间会导致消息无法发送到arduino
    wait_timeout = 2

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
        获取可用连接的串口
        :return comports: 串口字典
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
            serial = s.Serial(port, 9600, timeout=self.check_timeout)
        except Exception as e:
            raise e
        time.sleep(2)
        return serial

    def check_comports(self, serial_obj: s.Serial = None) -> bool:
        """
        检测arduino是否在此串口
        :param serial_obj:  串口对象
        """
        if self.com:
            serial_obj = self.new_serial_obj(self.com)
        self.send_msg(self.call_key, serial_obj)
        n = 0
        while n < self.check_timeout:
            res = self.read_msg(serial_obj)
            if res == self.check_key:
                self.serial = serial_obj
                logger.info(f"Arduino connected in port {serial_obj.name}!")
                return True
            time.sleep(1)
            n += 1
        return False

    def send_msg(self, msg: str, serial_obj: s.Serial = None) -> None:
        """
        通过串口发送消息
        :param msg: 信息
        :param serial_obj: 串口对象 如果没有默认使用类里的串口对象
        """
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
        if serial_obj and serial_obj.is_open:
            return d_utf8(serial_obj.read())
        elif self.serial and self.serial.is_open:
            return d_utf8(self.serial.read())


if __name__ == '__main__':
    serial_arduino = SerialArduino()
