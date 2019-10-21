import decimal
import logging
import time
from collections import defaultdict
from decimal import Decimal

import numpy as np
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import HttpResponse, render

from utils.limit_logger import LimitLogger

# 日志
logger = LimitLogger(logger=logging.getLogger('douban'))


def get_vote(url, headers):
    """获取评价人数"""

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    vote = soup.select('#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > a > span')[0].text
    time.sleep(0.1)
    return int(vote)


def get_base_data(tag_objs):
    """
    获取基准数据 - 去掉一个最大值和最小值，并求平均
        base_rate - 基准评分
        base_vote - 基准投票数
    """

    rates = [tag_obj['rate'] for tag_obj in tag_objs]
    votes = [tag_obj['vote'] for tag_obj in tag_objs]

    base_rate = np.mean(sorted(rates)[1:-1])
    base_vote = np.mean(sorted(votes)[1:-1]) * 0.75
    base_rate = Decimal(base_rate).quantize(Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
    base_vote = Decimal(base_vote).quantize(Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
    return base_rate, base_vote


# url解码
# from urllib import parse
#
# s = '%E7%83%AD%E9%97%A8'
# print(parse.unquote(s))

def grab_douban_tv():
    """抓取热门剧集"""

    # 初始化剧集类型和投票基数
    tags = ['美剧', '英剧', '韩剧', '日剧', '国产剧', '港剧', '日本动画', '综艺', '纪录片']

    headers = {
        "Host": "movie.douban.com",
        "Referer": "https://movie.douban.com/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    }

    url = 'https://movie.douban.com/j/search_subjects?'
    douban_tv_data = defaultdict(list)

    for tag in tags:
        print('开始筛选 【{}】...'.format(tag))
        payload = dict(type='tv', tag=tag, sort='recommend', page_limit=20, page_start=0)
        r = requests.get(url, headers=headers, params=payload)
        subjects = r.json()['subjects']

        # 收集剧集信息
        for subject in subjects:
            subject_title = subject['title']
            subject_rate = float(subject['rate'])
            subject_url = subject['url']
            subject_vote = get_vote(subject_url, headers)
            douban_tv_data[tag].append(
                {
                    'title': subject_title,
                    'rate': subject_rate,
                    'vote': subject_vote,
                    'url': subject_url
                }
            )
            print('【{}】信息已收集...'.format(subject_title))

        # 筛选达标剧集
        tag_objs = douban_tv_data[tag]
        base_rate, base_vote = get_base_data(tag_objs)

        tmp = []
        for tag_obj in tag_objs:
            rate = tag_obj['rate']
            vote = tag_obj['vote']
            if rate > base_rate and vote > base_vote:
                tmp.append(tag_obj)

        douban_tv_data[tag] = tmp

        print(22222, douban_tv_data)

    print('\n筛选完毕...')
    douban_tv_data = convert_data_format(douban_tv_data)
    # cache.delete_pattern("douban_tv_data")
    cache.delete("douban_tv_data")
    cache.set("douban_tv_data", douban_tv_data, timeout=7 * 24 * 60 * 60)


def convert_data_format(douban_tv_data):
    """转换数据格式 - 提供满足页面展示的数据格式"""

    result = []

    for tag, tag_objs in douban_tv_data.items():
        tmp = defaultdict(list)
        tmp['tag'] = tag

        for tag_obj in tag_objs:
            title = tag_obj['title']
            rate = tag_obj['rate']
            vote = tag_obj['vote']
            url = tag_obj['url']

            tmp['titles'].append(title)
            tmp['rates'].append(rate)
            tmp['votes'].append(vote)
            tmp['urls'].append(url)

        result.append(tmp)
    return result


# 定时任务调度
scheduler_search_db = BackgroundScheduler()
scheduler_search_db.add_job(grab_douban_tv, "cron", day_of_week='3', hour='3', minute='0')
scheduler_search_db.start()


def update_douban_tv_cache(request):
    """手动更新剧集缓存 - 被动更新"""
    if request.user.is_superuser:
        grab_douban_tv()
        return HttpResponse('剧集更新完毕！')
    return HttpResponseForbidden()


def show_douban_tv(request):
    """展示热门剧集"""

    douban_tv_data = cache.get('douban_tv_data')
    if douban_tv_data:
        return render(request, 'show_douban_tv.html', context={'douban_tv_data': douban_tv_data})
    else:
        logger.error('热门剧集缓存失效，请排查BackgroundScheduler和函数grab_douban_tv (可手动访问update_douban_tv_cache接口调试)')
        return HttpResponseNotFound()
