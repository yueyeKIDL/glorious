import random

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, HttpResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import csv
import getopt
import sys
import time
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

# from urllib.parse import quote, unquote, urlencode

# url解码
# decode_data = unquote('%E7%BE%8E%E5%89%A7')
# print(decode_data)


TAG_CONVERSION_DICT = dict(us='美剧', gb='英剧', kr='韩剧', jp='日剧', cn='国产剧', jpa='日本动画', df='纪录片')
headers = {
    "Host": "movie.douban.com",
    "Referer": "https://movie.douban.com/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Cookie": 'Cookie:bid=R_NjGlmHzLc; ll="108289"; __utmv=30149280.7162; douban-profile-remind=1; __guid=223695111.2801261442483869700.1555121081221.0579; __yadk_uid=su0b7K9g36n02VtPodU6bxjSmrqQNeVi; _vwo_uuid_v2=DA75957D9968A846830D702056248817A|624640ba21d7d6658c71f663d419f44e; douban-fav-remind=1; gr_user_id=d3b07b2b-f556-4601-b7a2-37f2cbe0d6fc; __gads=ID=af43163fe1df4ca9:T=1557648109:S=ALNI_MYSMPOl2Hkvn60cUHrt3jzyod7RSg; trc_cookie_storage=taboola%2520global%253Auser-id%3Db66f3e30-dd4d-429c-9e40-06a34397d236-tuct33c4874; viewed="30458408"; push_noty_num=0; push_doumail_num=0; acw_tc=276082a315682121587344277ee055770855b2bea693ff05b07c81730ed783; UM_distinctid=16d33142cca8c-08976d3fc7c8f8-3c604504-1fa400-16d33142ccb240; _ga=GA1.2.2035684642.1554454926; ct=y; Hm_lvt_16a14f3002af32bf3a75dfe352478639=1569908316; Hm_lvt_19fc7b106453f97b6a84d64302f21a04=1569911303; __utmc=30149280; __utmz=30149280.1570621121.45.25.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmc=223695111; dbcl2="71620970:jcZXXwrCkKA"; ck=7vt0; __utma=30149280.2035684642.1554454926.1570623176.1570625859.47; __utmt=1; __utmb=30149280.2.10.1570625859; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1570625862%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=223695111.1088930519.1555121082.1570623176.1570625862.35; __utmb=223695111.0.10.1570625862; __utmz=223695111.1570625862.35.28.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; monitor_count=18; _pk_id.100001.4cf6=4188bfc644de230d.1555121081.35.1570625864.1570623932.',
}


def output_help(filename):
    """控制台输出帮助说明"""

    print('标准命令 -> python {filename} -t <剧集类型> -r <评分> -v <评价人数> -n <筛选几个>'.format(filename=filename))
    print('-t 参数说明：us美剧,gb英剧,kr韩剧,jp日剧,cn国产剧,jpa日本动画,df纪录片')
    print('一个例子【搜索美剧】 -> python {filename} -t us -r 8.5 -v 10000 -n 3'.format(filename=filename))
    print('两个例子【搜索美剧、纪录片】 -> python {filename} -t us,df -r 8.5 -v 10000 -n 3'.format(filename=filename))
    print('=' * 90)
    print('简单命令 -> "python {filename}" 默认搜索所有种类、评分8.5以上、评价人数1w人以上的top3'.format(filename=filename))
    print('相当于 -> python {filename} -t us,gb,kr,jp,cn,jpa,df -r 8.5 -v 10000 -n 3'.format(filename=filename))
    print('=' * 90)
    print('缺省命令:全局默认搜索所有种类、评分8.5以上、评价人数1w人以上的top3，缺省参数按默认补全')
    print('一个例子 -> python {filename} -t us 相当于 python {filename} -t us -r 8.5 -v 10000 -n 3'.format(
        filename=filename))
    print('两个例子 -> python {filename} -t cn -n 5 相当于 -> python {filename} -t cn -n 5 -r 8.5 -v 10000'.format(
        filename=filename))


def output_result(result):
    """控制台输出筛选结果"""
    print('\n')
    print('筛选结果：')

    for index, (tag, items) in enumerate(result.items(), 1):
        print('\n')
        print('{index}.{tag}:'.format(index=index, tag=tag))
        for item in items:
            print("\t\t--标题:{title} - 地址:{url} - 评分:{rate} - 评价人数:{vote}".format(title=item[0], url=item[1],
                                                                                 rate=item[2], vote=item[3]))


def get_vote(url):
    """获取评价人数"""

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    votes = soup.select('#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > a > span')[0].text
    return votes


def get_popular_tv_series(result, **kwargs):
    """获取热门电视剧集"""

    tag = kwargs.pop('tag')
    rate = kwargs.pop('rate')
    vote = kwargs.pop('vote')
    nums = kwargs.pop('nums')

    payload = dict(type='tv', tag=tag, sort='recommend', page_limit=20, page_start=0)
    url = 'https://movie.douban.com/j/search_subjects?'

    # 选出每个剧集类型下的top n（最多筛选3页）
    while len(result[tag]) < nums and payload['page_start'] < 80:
        time.sleep(0.1)
        r = requests.get(url, headers=headers, params=payload)
        subjects = r.json().get('subjects')
        for subject in subjects:
            if len(result[tag]) >= nums:
                break
            subject_title = subject['title']
            subject_rate = subject['rate']
            subject_url = subject.get('url')
            time.sleep(0.1)
            subject_vote = get_vote(subject_url)

            # 按评分、评论人数筛选
            if float(subject_rate) >= rate and int(subject_vote) >= vote:
                data = (tag, subject_title, subject_url, subject_rate, subject_vote)
                result[tag].append(data)

                print('\n')
                print('入选一个【{tag}】'.format(tag=tag))
                print("标题:{title} - 地址:{url} - 评分:{rate} - 评价人数:{vote}".format(title=subject_title, url=subject_url,
                                                                               rate=subject_vote, vote=subject_vote))
                print('=' * 90)
        else:
            payload['page_start'] += 20


def conver_tags(abbr_tags):
    """剧集类型英中转换"""

    try:
        arg = [TAG_CONVERSION_DICT[abbr_tag] for abbr_tag in abbr_tags]
    except KeyError as e:
        print('Warning!!! -t 参数有误', e)
        sys.exit(2)
    return arg


def get_standard_args():
    """
    获取控制台标准参数:
        -t 剧集类型（tag）
        -r 评分（rate）
        -v 评价人数（vote）
        -n 筛选几个（nums）
    """
    data = {}
    filename = sys.argv[0]
    console_args = sys.argv[1:]
    try:
        opts, other_args = getopt.getopt(console_args, "t:r:v:n:", ["help"])
        # print(f'opts:{opts}')
        # print(f'args:{other_args}')
    except getopt.GetoptError:
        print('COMMAND ERROR!!!')
        print('一个例子 -> python {filename} -t us -r 8.5 -v 10000 -n 3'.format(filename=filename))
        print('查看帮助 -> python {filename} --help'.format(filename=filename))
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            output_help(filename)
            sys.exit()

        if opt == '-t':
            abbr_tags = arg.split(',')
            arg = conver_tags(abbr_tags)  # 剧集类型英中转换
        data.update({opt: arg})
    return data


def save_to_csv(result):
    csv_headers = ['类型', '标题', '网址', '评分', '评价人数']
    csv_rows = []
    for items in result.values():
        csv_rows.extend(items)

    with open('popular_douban_tv.csv', 'w', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(csv_headers)
        f_csv.writerows(csv_rows)


def main():
    # 获取控制台标准参数
    data = get_standard_args()

    # 缺省值
    tags = data.get('-t', ['美剧'])
    try:
        rate = float(data.get('-r', 7.5))
        vote = int(data.get('-v', 10000))
        nums = int(data.get('-n', 4))
    except ValueError as e:
        print('Warning!!! 参数有误', e)
        sys.exit(2)
    result = defaultdict(list)
    # 按不同剧集类型抓取
    for tag in tags:
        print('\n')
        print('开始筛选【{tag}】...'.format(tag=tag))

        get_popular_tv_series(result, tag=tag, rate=rate, vote=vote, nums=nums)
    return result


# Create your views here.
# @cache_page(60 * 15)
def index(request):
    # result = main()
    # tags = result.keys()
    # _, titles, urls, rates, votes = [list(i) for i in zip(*result['美剧'])]
    # print(111111, tags, titles, urls, rates, votes)
    # rates = [float(i) for i in rates]
    # votes = [float(i) for i in votes]
    ss = [
        {'tag': '美剧', 'titles': ['大青蛙大全', '亲卫队请问', '全微分给'], 'rates': [9.6, 7.5, 8.1], 'votes': [21000, 17500, 25000]},
        {'tag': '日剧', 'titles': ['大青蛙大全', '亲卫队请问', '全微分给'], 'rates': [9.6, 7.5, 8.1], 'votes': [21000, 17500, 25000]},
        {'tag': '韩剧', 'titles': ['大青蛙大全', '亲卫队请问', '全微分给'], 'rates': [9.6, 7.5, 8.1], 'votes': [21000, 17500, 25000]},
    ]
    return render(request, 'index.html', locals())


def redis_keys(request):
    print(cache.keys('*'))
    return HttpResponse(cache.keys('*'))
