import logging

logger = logging.getLogger('douban')

try:
    1 / 0
except Exception as e:
    logger.exception(e)
print('gogogo')
