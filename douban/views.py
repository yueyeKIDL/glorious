import random

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, HttpResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache


# Create your views here.
# @cache_page(60 * 15)
def index(request):
    # headers = {
    #     "Host": "movie.douban.com",
    #     "Referer": "https://movie.douban.com/",
    #     "Upgrade-Insecure-Requests": "1",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    #     # "Cookie": 'Cookie:bid=R_NjGlmHzLc; ll="108289"; __utmv=30149280.7162; douban-profile-remind=1; __guid=223695111.2801261442483869700.1555121081221.0579; __yadk_uid=su0b7K9g36n02VtPodU6bxjSmrqQNeVi; _vwo_uuid_v2=DA75957D9968A846830D702056248817A|624640ba21d7d6658c71f663d419f44e; douban-fav-remind=1; gr_user_id=d3b07b2b-f556-4601-b7a2-37f2cbe0d6fc; __gads=ID=af43163fe1df4ca9:T=1557648109:S=ALNI_MYSMPOl2Hkvn60cUHrt3jzyod7RSg; trc_cookie_storage=taboola%2520global%253Auser-id%3Db66f3e30-dd4d-429c-9e40-06a34397d236-tuct33c4874; viewed="30458408"; push_noty_num=0; push_doumail_num=0; acw_tc=276082a315682121587344277ee055770855b2bea693ff05b07c81730ed783; UM_distinctid=16d33142cca8c-08976d3fc7c8f8-3c604504-1fa400-16d33142ccb240; _ga=GA1.2.2035684642.1554454926; ct=y; Hm_lvt_16a14f3002af32bf3a75dfe352478639=1569908316; Hm_lvt_19fc7b106453f97b6a84d64302f21a04=1569911303; __utmc=30149280; __utmz=30149280.1570621121.45.25.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmc=223695111; dbcl2="71620970:jcZXXwrCkKA"; ck=7vt0; __utma=30149280.2035684642.1554454926.1570623176.1570625859.47; __utmt=1; __utmb=30149280.2.10.1570625859; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1570625862%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=223695111.1088930519.1555121082.1570623176.1570625862.35; __utmb=223695111.0.10.1570625862; __utmz=223695111.1570625862.35.28.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; monitor_count=18; _pk_id.100001.4cf6=4188bfc644de230d.1555121081.35.1570625864.1570623932.',
    # }
    #
    # random_nums = [30279863, 33385536, 30401122, 30156074]
    #
    # url = 'https://movie.douban.com/subject/{}/?tag=%E7%83%AD%E9%97%A8&from=gaia'.format(str(random.choice(random_nums)))
    #
    # # 爬虫随机数
    # r = requests.get(url, headers=headers)
    # soup = BeautifulSoup(r.text, 'lxml')
    # votes = soup.select('#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > a > span')[0].text
    # print(votes)
    return render(request, 'zuanqu_index.html')


def redis_keys(request):
    print(cache.keys('*'))
    return HttpResponse(cache.keys('*'))