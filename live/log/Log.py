import logging
import os
import time
from datetime import datetime
from typing import Dict

LOGGER_LEVEL: Dict[str, int] = {
    "RESET": -10,
    "SUCCESS": 0,
    "NOTSET": 0,
    "DEBUG": 10,
    "INFO": 20,

    "WARN": 30,
    "WARNING": 30,
    "ERROR": 40,
    "FATAL": 50,
    "CRITICAL": 50,
}

COLORS: Dict[LOGGER_LEVEL, str] = {
    LOGGER_LEVEL["ERROR"]: "\033[91m",
    LOGGER_LEVEL["SUCCESS"]: "\033[92m",
    LOGGER_LEVEL["WARN"]: "\033[93m",
    LOGGER_LEVEL["WARNING"]: "\033[93m",
    LOGGER_LEVEL["INFO"]: "\033[94m",

    LOGGER_LEVEL["CRITICAL"]: "\033[95m",
    LOGGER_LEVEL["FATAL"]: "\033[95m",
    LOGGER_LEVEL["DEBUG"]: "",
    LOGGER_LEVEL["NOTSET"]: "",
    LOGGER_LEVEL["RESET"]: "\033[0m"
}
LEVEL_NAME: Dict[LOGGER_LEVEL, str] = {
    LOGGER_LEVEL["ERROR"]: "ERROR",
    LOGGER_LEVEL["SUCCESS"]: "SUCCESS",
    LOGGER_LEVEL["WARN"]: "WARNING",
    LOGGER_LEVEL["WARNING"]: "WARNING",
    LOGGER_LEVEL["INFO"]: "INFO",

    LOGGER_LEVEL["CRITICAL"]: "CRITICAL",
    LOGGER_LEVEL["FATAL"]: "CRITICAL",
    LOGGER_LEVEL["DEBUG"]: "NOTSET",
    LOGGER_LEVEL["NOTSET"]: "NOTSET",
    LOGGER_LEVEL["RESET"]: "RESET",
}


class Logger:

    def __init__(self, logger_name="yzl_danmaku_logger"):
        # 创建日志器
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(LOGGER_LEVEL["DEBUG"])

        # 存到logs/{时间日期}.log
        if not os.path.exists('logs'):
            os.mkdir('logs')

        log_file = os.path.join('logs', time.strftime('%Y-%m-%d %H-%M-%S', time.localtime()) + '.log')

        # 创建文件处理器并设置编码为 UTF-8
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(LOGGER_LEVEL["DEBUG"])

        # 创建日志格式
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # 添加处理器到日志器
        self.logger.addHandler(file_handler)

        self._write_log(LOGGER_LEVEL["INFO"], "日志器初始化成功")

    def _write_log(self, logger_level: LOGGER_LEVEL = LOGGER_LEVEL["DEBUG"], *args):
        level = LEVEL_NAME[logger_level]
        logger_level = LOGGER_LEVEL[level]
        # 获取当前日期
        formatted_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color = COLORS.get(level, COLORS["RESET"])
        msg = "\t".join(map(str, args))

        # 带颜色的消息用于控制台输出
        colored_message = f"{color}[{formatted_datetime}] [{level}] {msg}{COLORS['RESET']}"

        # 输出到控制台
        print(colored_message)

        # 不带颜色的消息用于写入日志文件
        log_message = f"[{formatted_datetime}] [{level}] {msg}"
        self.logger.log(level=logger_level, msg=log_message)
        pass

    def success(self, *msg):
        self._write_log(LOGGER_LEVEL["SUCCESS"], msg)

    def info(self, *msg):
        self._write_log(LOGGER_LEVEL["INFO"], *msg)

    def warning(self, *msg):
        self._write_log(LOGGER_LEVEL["WARNING"], *msg)

    def error(self, *msg):
        self._write_log(LOGGER_LEVEL["ERROR"], *msg)

    def critical(self, *msg):
        self._write_log(LOGGER_LEVEL["CRITICAL"], *msg)

    def debug(self, *msg):
        self._write_log(LOGGER_LEVEL["DEBUG"], *msg)
