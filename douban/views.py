import logging
import time
from collections import defaultdict

import numpy as np
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, HttpResponse

# 日志
logger = logging.getLogger('douban')


def get_vote(url, headers):
    """获取评价人数"""

    time.sleep(0.1)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    vote = soup.select('#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > a > span')[0].text
    return int(vote)


def get_base_rate(subjects):
    """获取基准评分 - 当前页面所有剧集的平均分"""

    rates = []
    for subject in subjects:
        rate = float(subject['rate'])
        rates.append(rate)
    base_rate = np.mean(rates)
    return base_rate


# url解码
# from urllib import parse
#
# s = '%E7%83%AD%E9%97%A8'
# print(parse.unquote(s))

def grab_douban_tv():
    """抓取热门剧集"""

    # 初始化剧集类型和投票基数
    tags = ['美剧', '英剧', '韩剧', '日剧', '国产剧', '港剧', '日本动画', '综艺', '纪录片']
    base_vote = 10000

    headers = {
        "Host": "movie.douban.com",
        "Referer": "https://movie.douban.com/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    }

    url = 'https://movie.douban.com/j/search_subjects?'
    douban_tv_data = []

    for tag in tags:
        print('开始筛选 【{}】...'.format(tag))
        payload = dict(type='tv', tag=tag, sort='recommend', page_limit=20, page_start=0)
        r = requests.get(url, headers=headers, params=payload)
        subjects = r.json()['subjects']
        base_rate = get_base_rate(subjects)
        if not base_rate:
            break
        titles = defaultdict(list)
        rates = defaultdict(list)
        votes = defaultdict(list)
        for subject in subjects:

            subject_title = subject['title']
            subject_rate = float(subject['rate'])
            subject_url = subject['url']

            # 大于基准分，抓取其vote
            if subject_rate > base_rate:
                subject_vote = get_vote(subject_url, headers)

                # 保存该tag类型的标题、评分、投票数
                if subject_vote > base_vote:
                    titles['titles'].append(subject_title)
                    rates['rates'].append(subject_rate)
                    votes['votes'].append(subject_vote)

                    print('【{}】入选...'.format(subject_title))

        temp_data = {'tag': tag, **titles, **rates, **votes}

        # 未筛选出剧集,不保存数据
        if len(temp_data) > 1:
            douban_tv_data.append(temp_data)
    cache.delete_pattern("douban_tv_data")
    cache.set("douban_tv_data", douban_tv_data, timeout=7 * 24 * 60 * 60)


# 定时任务调度
scheduler_search_db = BackgroundScheduler()
scheduler_search_db.add_job(grab_douban_tv, "cron", day_of_week='3', hour='3', minute='0')
scheduler_search_db.start()


def update_douban_tv_cache(request):
    """手动更新剧集缓存 - 被动更新"""
    if request.user.is_superuser:
        grab_douban_tv()
        return HttpResponse('更新完毕！')
    return HttpResponseForbidden()


def show_douban_tv(request):
    """展示热门剧集"""

    douban_tv_data = cache.get('douban_tv_data')
    if douban_tv_data:
        return render(request, 'show_douban_tv.html', context={'douban_tv_data': douban_tv_data})
    else:
        logger.warning('热门剧集缓存失效，请排查定时调度机制和函数grab_douban_tv')
        return HttpResponseNotFound()
