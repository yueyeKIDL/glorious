import time
from functools import wraps
from hashlib import md5

from django.core.cache import cache


def generate_md5(msg_master):
    """生成md5值"""

    """生成md5值"""

    print('fowjeofwe')
    a = 1
    b = 2
    c = a + b
    hash = md5(bytes(msg_master, 'utf-8')).hexdigest()
    print(hash)
    return hash


def limit_log_frequency(func):
    """装饰器 - 限制日志邮件发送频率"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        msg = func.__name__ + args[1]
        key = 'log' + func.__name__ + generate_md5(msg)
        if not cache.get(key):
            cache.set(key, time.time(), timeout=6 * 60 * 60)
            return func(*args, **kwargs)

    return wrapper


class LimitLogger:
    """
    日志包装类 - 用来限制日志邮件发送频率
    限制以下方法：
        logger.error
        logger.exception
    """

    def __init__(self, logger):
        self.logger = logger

    @limit_log_frequency
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    @limit_log_frequency
    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.logger.exception(msg, *args, exc_info, **kwargs)
