"""
    @Author: ImYrS Yang
    @Date: 2023/6/27
    @Copyright: @ImYrS
"""


class LoginRequestState:
    Unknown = -1
    Pending = 0  # 等待扫码
    Scanned = 10  # 已扫码, 等待登录
    Confirmed = 20  # 已登录
    Expired = 30  # 已过期
    Canceled = 40  # 已取消登录
