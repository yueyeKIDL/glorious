import decimal
import logging
import time
from collections import defaultdict
from decimal import Decimal
from operator import itemgetter

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

headers = {
    'Cookie': 'bid=R_NjGlmHzLc; ll="108289"; __utmv=30149280.7162; douban-profile-remind=1; __guid=223695111.2801261442483869700.1555121081221.0579; __yadk_uid=su0b7K9g36n02VtPodU6bxjSmrqQNeVi; _vwo_uuid_v2=DA75957D9968A846830D702056248817A|624640ba21d7d6658c71f663d419f44e; douban-fav-remind=1; gr_user_id=d3b07b2b-f556-4601-b7a2-37f2cbe0d6fc; __gads=ID=af43163fe1df4ca9:T=1557648109:S=ALNI_MYSMPOl2Hkvn60cUHrt3jzyod7RSg; trc_cookie_storage=taboola%2520global%253Auser-id%3Db66f3e30-dd4d-429c-9e40-06a34397d236-tuct33c4874; viewed="30458408"; push_noty_num=0; push_doumail_num=0; UM_distinctid=16d33142cca8c-08976d3fc7c8f8-3c604504-1fa400-16d33142ccb240; _ga=GA1.2.2035684642.1554454926; ct=y; Hm_lvt_16a14f3002af32bf3a75dfe352478639=1569908316; Hm_lvt_19fc7b106453f97b6a84d64302f21a04=1569911303; dbcl2="71620970:2HsyGJY0rLE"; ck=vc6W; __utmc=30149280; __utmc=223695111; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1572151618%2C%22https%3A%2F%2Fbook.douban.com%2Fchart%3Ficn%3Dindex-topchart-nonfiction%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.2035684642.1554454926.1572147866.1572151618.57; __utmz=30149280.1572151618.57.29.utmcsr=book.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/chart; __utma=223695111.1088930519.1555121082.1572149770.1572151618.43; __utmb=223695111.0.10.1572151618; __utmz=223695111.1572151618.43.36.utmcsr=book.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/chart; _pk_id.100001.4cf6=4188bfc644de230d.1555121081.43.1572151711.1572149770.; __utmb=30149280.2.10.1572151618; monitor_count=10',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
}


def get_vote(url, session):
    """获取评价人数"""

    r = session.get(url)
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


def get_tag_page_json(tag, session):
    """获取当前剧集页返回json信息"""

    print('开始筛选 【{}】...'.format(tag))
    url = 'https://movie.douban.com/j/search_subjects?'
    payload = dict(type='tv', tag=tag, sort='recommend', page_limit=20, page_start=0)
    r = session.get(url, params=payload)
    subjects = r.json()['subjects']
    return subjects


def collect_tv_data(douban_tv_data, tag, subjects, session):
    """收集剧集信息"""

    for subject in subjects:
        subject_title = subject['title']
        subject_rate = float(subject['rate'])
        subject_url = subject['url']

        # 获取投票数
        subject_vote = get_vote(subject_url, session)
        douban_tv_data[tag].append(
            {
                'title': subject_title,
                'rate': subject_rate,
                'vote': subject_vote,
                'url': subject_url
            }
        )
        print('【{}】信息已收集...'.format(subject_title))
    return douban_tv_data


def filter_tv_series(douban_tv_data, tag):
    """筛选达标剧集"""

    tag_objs = douban_tv_data[tag]

    # 获取基准数据
    base_rate, base_vote = get_base_data(tag_objs)

    tmp = []
    for tag_obj in tag_objs:
        rate = tag_obj['rate']
        vote = tag_obj['vote']
        if rate > base_rate and vote > base_vote:
            tmp.append(tag_obj)

    douban_tv_data[tag] = tmp
    return douban_tv_data


def convert_data_format(douban_tv_data):
    """
    转换数据格式 - 提供满足页面展示的数据格式
    input:
    {
        tag: [
            {'title': title, 'url': url, 'rate': rate, 'vote': vote},
            {...},
            {...},
        ]
    }
    output:
    [
        {'tag': tag, 'titles': ['xx', 'xx'], 'urls': ['xx', 'xx'], 'rates': ['xx', 'xx'], 'vote': ['xx', 'xx']},
        {...},
        {...},
    ]

    """

    result = []

    for tag, tag_objs in douban_tv_data.items():
        tmp = defaultdict(list)
        tmp['tag'] = tag

        for tag_obj in tag_objs:
            title = tag_obj['title']
            url = tag_obj['url']
            rate = tag_obj['rate']
            vote = tag_obj['vote']

            tmp['titles'].append(title)
            tmp['rates'].append(rate)
            tmp['votes'].append(vote)
            tmp['urls'].append(url)

        result.append(tmp)
    return result


def grab_douban_tv():
    """抓取热门剧集"""

    # 初始化剧集类型和投票基数
    tags = ['美剧', '英剧', '韩剧', '日剧', '国产剧', '港剧', '日本动画', '综艺', '纪录片']
    douban_tv_data = defaultdict(list)
    session = requests.Session()
    session.get('https://www.douban.com/', headers=headers)

    for tag in tags:
        # 获取当前剧集页返回json信息
        subjects = get_tag_page_json(tag, session)

        # 收集剧集信息
        douban_tv_data = collect_tv_data(douban_tv_data, tag, subjects, session)

        # 筛选达标剧集
        douban_tv_data = filter_tv_series(douban_tv_data, tag)
        douban_tv_data[tag].sort(key=itemgetter('rate'), reverse=True)

    print('\n筛选完毕...')
    douban_tv_data = convert_data_format(douban_tv_data)

    # redis cache
    # cache.delete_pattern("douban_tv_data")

    cache.delete("douban_tv_data")
    cache.set("douban_tv_data", douban_tv_data, timeout=7 * 24 * 60 * 60)


def vote_format(vote_str):
    """评价人数格式化"""

    vote = vote_str.split('人')[0][1:]
    return int(vote)


def grab_douban_books():
    """抓取热门图书"""

    book_urls = {
        '虚构类书籍': 'https://book.douban.com/chart?subcat=F&icn=index-topchart-fiction',
        '非虚构类书籍': 'https://book.douban.com/chart?icn=index-topchart-nonfiction',
    }
    douban_book_data = []

    for tag, url in book_urls.items():
        # 抓取数据
        print('\n开始抓取 【{}书籍】...'.format(tag))
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        titles_html = soup.select('#content > div > div.article > ul > li > div.media__body > h2 > a')
        urls_html = soup.select('#content > div > div.article > ul > li > div.media__body > h2 > a')
        rates_html = soup.select('#content > div > div.article > ul > li > div.media__body > p.clearfix.w250 '
                                 '> span.font-small.color-red.fleft')
        votes_html = soup.select('#content > div > div.article > ul > li > div.media__body > p.clearfix.w250 '
                                 '> span.fleft.ml8.color-gray')

        # 数据整形
        titles = [title_html.get_text() for title_html in titles_html]
        urls = [url_html.get('href') for url_html in urls_html]
        rates = [float(rate_html.get_text()) for rate_html in rates_html]
        votes = [vote_format(vote_html.get_text()) for vote_html in votes_html]

        tmp = [dict(title=title, url=url, rate=rate, vote=vote) for title, url, rate, vote in
               zip(titles, urls, rates, votes)]

        # 按评分排序
        tmp = convert_data_format({tag: sorted(tmp, key=itemgetter('rate'), reverse=True)})

        # 保存数据
        douban_book_data.extend(tmp)

    print('\n抓取完毕...')
    cache.delete("douban_books_data")
    cache.set("douban_books_data", douban_book_data, timeout=7 * 24 * 60 * 60)


# 定时任务调度
scheduler_search_db = BackgroundScheduler()
scheduler_search_db.add_job(grab_douban_tv, "cron", day_of_week='3', hour='3', minute='0')
scheduler_search_db.add_job(grab_douban_books, "cron", day_of_week='1', hour='3', minute='0')
scheduler_search_db.start()


def update_douban_tv_cache(request):
    """手动更新剧集缓存 - 被动更新"""

    if request.user.is_superuser:
        grab_douban_tv()
        return HttpResponse('剧集更新完毕！')
    return HttpResponseForbidden()


def update_douban_books_cache(request):
    """手动更新图书缓存 - 被动更新"""

    if request.user.is_superuser:
        grab_douban_books()
        return HttpResponse('图书更新完毕！')
    return HttpResponseForbidden()


def show_douban_tv(request):
    """展示热门剧集"""

    douban_tv_data = cache.get('douban_tv_data')
    if douban_tv_data:
        return render(request, 'show_douban_tv.html', context={'douban_tv_data': douban_tv_data})
    else:
        logger.error('热门剧集缓存失效，请排查BackgroundScheduler和函数grab_douban_tv(可手动访问update_douban_tv_cache接口调试)')
        return HttpResponseNotFound()


def show_douban_books(request):
    """展示热门书籍"""

    douban_books_data = cache.get('douban_books_data')
    if douban_books_data:
        return render(request, 'show_douban_books.html', context={'douban_books_data': douban_books_data})
    else:
        logger.error('热门书籍缓存失效，请排查BackgroundScheduler和函数grab_douban_books(可手动访问update_douban_books_cache接口调试)')
        return HttpResponseNotFound()
