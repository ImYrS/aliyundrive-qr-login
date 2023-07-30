"""
    @Author: ImYrS Yang
    @Date: 2023/2/12
    @Copyright: ImYrS Yang
    @Description: 
"""

import hashlib
import os
import random
import re
import string
import time
from typing import NoReturn, Optional, Iterable, Any


def formatted_time(
        time_stamp: Optional[int] = int(time.time()),
        secure_format: Optional[bool] = False,
) -> str:
    """
    时间戳转换为格式化时间

    :param time_stamp: 需要格式化的 Unix 时间戳
    :param secure_format: 是否需要安全的字符格式
    :return: 格式化后的时间
    """
    return (
        time.strftime("%Y%m%d_%H%M%S", time.localtime(time_stamp))
        if secure_format
        else time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))
    )


def timestamp(ms: Optional[bool] = True) -> int:
    """
    获取当前时间戳

    :param ms: 是否以毫秒为单位
    :return: 时间戳
    """
    return int(time.time()) if not ms else int(time.time() * 1000)


def get_today_timestamp() -> int:
    """
    获取今天 0 点的时间戳

    :return: 时间戳, 单位毫秒
    """
    return int(time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")) * 1000)


def now() -> int:
    """获取毫秒单位时间戳的别名"""
    return timestamp()


def calc_time(t: int) -> dict:
    """
    计算时间长度

    :param t: 时长, 单位秒
    :return: dict 格式化后的时长
    """
    result = {"day": 0, "hour": 0, "minute": 0, "second": 0}
    if t >= (3600 * 24):
        result["day"] = t // (3600 * 24)
        t %= 3600 * 24
    if t >= 3600:
        result["hour"] = t // 3600
        t %= 3600
    if t >= 60:
        result["minute"] = t // 60
        t %= 60
    result["second"] = t
    return result


def rand_char(length=32, upper=False) -> str:
    """
    生成随机字符串

    :param length: 字符串长度
    :param upper: 是否为全大写
    :return:
    """
    # 数字 + 英文字母
    char = string.digits + string.ascii_letters
    if length > len(char):
        result = ""
        count = length
        while True:
            if count == 0:
                break

            if count > len(char):
                result += "".join(random.sample(char, len(char)))
                count -= len(char)
            else:
                result += "".join(random.sample(char, count))
                count -= count
    else:
        result = "".join(random.sample(char, length))

    # 是否大写
    if upper:
        return result.upper()
    else:
        return result


def rand_number(length=6) -> str:
    """
    生成随机数字

    :param length: 字符串长度
    :return:
    """
    if length > len(string.digits):
        result = ""
        count = length
        while True:
            if count == 0:
                break

            if count > len(string.digits):
                result += "".join(random.sample(string.digits, len(string.digits)))
                count -= len(string.digits)
            else:
                result += "".join(random.sample(string.digits, count))
                count -= count
    else:
        result = "".join(random.sample(string.digits, length))

    return result


def hash256(data) -> str:
    """
    SHA-256 加密

    :param data: 需要加密的数据
    :return: 加密后的数据
    """
    try:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    except AttributeError:
        return hashlib.sha256(data).hexdigest()


def hash512(data) -> str:
    """
    SHA-512 加密

    :param data: 需要加密的数据
    :return: 加密后的数据
    """
    try:
        return hashlib.sha512(data.encode("utf-8")).hexdigest()
    except AttributeError:
        return hashlib.sha512(data).hexdigest()


def mkdir(path) -> NoReturn:
    """
    创建文件夹, 支持多级

    :param path: 文件夹路径
    :return:
    """
    try:
        os.mkdir(path)
    except FileNotFoundError:
        split = path.split("/")
        for i in range(len(split)):
            if split[i] == ".":
                continue
            try:
                os.mkdir(path.rsplit("/", len(split) - (i + 1))[0])
            except FileExistsError:
                pass
    except FileExistsError:
        pass


def str_process(var):
    """字符串处理, 支持列表和字典"""
    if type(var) in [int, float, bool, None]:
        return var
    elif type(var) is str:
        return clean_str(var)
    elif type(var) in [list, tuple]:
        return [str_process(i) for i in var]
    elif type(var) is dict:
        return {str_process(k): str_process(v) for k, v in var.items()}
    else:
        return var


def clean_str(text: str) -> str:
    """去除异常字符"""
    text = eval(re.sub(r"\\u.{4}", "", repr(text)))  # 去除 unicode 编码
    text = eval(re.sub(r"\\x.{2}", "", repr(text)))  # 去除 hex 编码
    text = eval(re.sub(r"\\", "", repr(text)))  # 去除转义字符
    text = eval(re.sub(r"\"", "", repr(text)))  # 去除双引号
    text = eval(re.sub(r"\n", "", repr(text)))  # 去除换行符
    text = eval(re.sub(r"\r", "", repr(text)))  # 去除回车符
    text = eval(re.sub(r"\t", "", repr(text)))  # 去除制表符
    text = eval(re.sub(r"\s", "", repr(text)))  # 去除空格

    # 全角转半角
    new_string = ""
    for char in text:
        inside_code = ord(char)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xFEE0

        # 不是半角字符返回原来的字符
        new_string += (
            char if inside_code < 0x0020 or inside_code > 0x7E else chr(inside_code)
        )

    return new_string


def size_format(size: int) -> str:
    """
    格式化文件大小

    :param size: 文件大小
    :return: str 格式化后的文件大小
    """
    if size < 1024:
        return str(size) + " B"
    elif size < 1024 * 1024:
        return str(round(size / 1024, 2)) + " KB"
    elif size < 1024 * 1024 * 1024:
        return str(round(size / 1024 / 1024, 2)) + " MB"
    elif size < 1024 * 1024 * 1024 * 1024:
        return str(round(size / 1024 / 1024 / 1024, 2)) + " GB"
    elif size < 1024 * 1024 * 1024 * 1024 * 1024:
        return str(round(size / 1024 / 1024 / 1024 / 1024, 2)) + " TB"
    else:
        return str(round(size / 1024 / 1024 / 1024 / 1024 / 1024, 2)) + " PB"


def get_dir_size(path: str) -> int:
    """
    获取文件夹大小

    :param path: 文件夹路径
    :return: int 文件夹大小
    """
    size = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            size += os.path.getsize(os.path.join(root, file))
    return size


def get_real_ip(headers: Optional[Iterable[Any]] = None) -> str:
    """
    在使用了反向代理或 CDN 等情况下, 获取请求真实 IP

    :param headers: 可迭代的请求头
    :return: IP 或 127.0.0.1
    """
    probable_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Forwarded',
        'Forwarded-For',
        'Forwarded',
        'True-Client-IP',
        'Client-IP',
        'Ali-CDN-Real-Ip',
        'Cdn-Src-Ip',
        'Cdn-Real-Ip',
        'Cf-Connecting-Ip',
        'X-Cluster-Client-Ip',
        'Wl-Proxy-Client-Ip',
        'Proxy-Client-IP',
        'True-Client-Ip',
    ]

    existed_headers = {}
    for k, v in headers:
        existed_headers[k.upper()] = v

    for header in probable_headers:
        if header.upper() in existed_headers:
            ip = existed_headers[header.upper()]

            # 可能存在多个 IP, 取第一个
            return (
                ip
                if ',' not in ip
                else ip.split(',')[0]
            )

    return '127.0.0.1'
