import sys
import getopt

import time
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from urllib.parse import quote, unquote, urlencode


# url解码
# decode_data = unquote('%E7%BE%8E%E5%89%A7')
# print(decode_data)


def get_vote(url):
    """获取评价人数"""

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    votes = soup.select('#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > a > span')[0].text
    return votes


def get_popular_tv_series(**kwargs):
    """获取热门电视剧集"""

    tag = kwargs.pop('tag')
    rate = kwargs.pop('rate')
    vote = kwargs.pop('vote')
    nums = kwargs.pop('nums')

    payload = dict(type='tv', tag=tag, sort='recommend', page_limit=20, page_start=0)
    url = 'https://movie.douban.com/j/search_subjects?'

    # 选出每个剧集类型下的top n（最多筛选3页）
    while len(result[tag]) < nums and payload['page_start'] < 80:
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
                data = f"--标题:{subject_title} - 地址:{subject_url} - 评分:{subject_rate} - 评价人数:{subject_vote}"
                result[tag].append(data)

                print('\n')
                print(f'入选一个【{tag}】')
                print(f"标题:{subject_title} - 地址:{subject_url} - 评分:{subject_rate} - 评价人数:{subject_vote}")
                print('=' * 90)
        else:
            payload['page_start'] += 20


def get_standard_args():
    """
    获取控制台标准参数:
        -t 剧集类型（tag）
        -r 评分（rate）
        -v 评价人数（vote）
        -n 筛选几个（nums）
    """
    try:
        data = {}
        filename = sys.argv[0]
        console_args = sys.argv[1:]
        opts, other_args = getopt.getopt(console_args, "t:r:v:n:", ["help"])
        # print(f'opts:{opts}')
        # print(f'args:{other_args}')
    except getopt.GetoptError:
        print('COMMAND ERROR!!!')
        print(f'一个例子 -> python {filename} -t us -r 8.5 -v 10000 -n 3')
        print(f'查看帮助 -> python {filename} --help')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            print(f'标准命令 -> python {filename} -t <剧集类型> -r <评分> -v <评价人数> -n <筛选几个>')
            print('-t 参数说明：us美剧,gb英剧,kr韩剧,jp日剧,cn国产剧,jpa日本动画,df纪录片')
            print(f'一个例子【搜索美剧】 -> python {filename} -t us -r 8.5 -v 10000 -n 3')
            print(f'两个例子【搜索美剧、纪录片】 -> python {filename} -t us,df -r 8.5 -v 10000 -n 3')
            print('=' * 90)
            print(f'简单命令 -> "python {filename}" 默认搜索所有种类、评分8.5以上、评价人数1w人以上的top3')
            print(f'相当于 -> python {filename} -t us,gb,kr,jp,cn,jpa,df -r 8.5 -v 10000 -n 3')
            print('=' * 90)
            print('缺省命令:全局默认搜索所有种类、评分8.5以上、评价人数1w人以上的top3，缺省参数按默认补全')
            print(f'一个例子 -> python {filename} -t us 相当于 python {filename} -t us -r 8.5 -v 10000 -n 3')
            print(f'两个例子 -> python {filename} -t cn -n 5 相当于 -> python {filename} -t cn -n 5 -r 8.5 -v 10000')
            sys.exit()

        # 处理多剧集类型
        if opt == '-t':
            arg = arg.split(',')
            for i in arg:
                if i not in ('us', 'gb', 'kr', 'jp', 'cn', 'jpa', 'df'):
                    print('Warning!!! -t 参数有误')
                    sys.exit(2)
        data.update({opt: arg})
    return data


def main():
    tags = ['美剧', '英剧', '韩剧', '日剧', '国产剧', '日本动画', '纪录片']

    # 获取控制台标准参数
    data = get_standard_args()

    # 字典-t剧集类型中英转化
    en_tags = data.get('-t')
    if en_tags:
        d = dict(us='美剧', gb='英剧', kr='韩剧', jp='日剧', cn='国产剧', jpa='日本动画', df='纪录片', )
        tags = [d[en_tag] for en_tag in en_tags]

    # 缺省值
    rate = float(data.get('-r', 8.5))
    vote = int(data.get('-v', 10000))
    nums = int(data.get('-n', 3))

    # 抓取每种剧集类型
    for tag in tags:
        print('\n')
        print(f'开始筛选【{tag}】...')

        # 开始抓取
        get_popular_tv_series(tag=tag, rate=rate, vote=vote, nums=nums)

    # 输出结果
    print('\n')
    print('筛选结果：')

    for index, (key, items) in enumerate(result.items(), 1):
        print('\n')
        print(f'{index}.{key}:')
        for item in items:
            print(f'\t\t{item}')


if __name__ == "__main__":
    # 初始化
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/63.0.3239.132 Safari/537.36"}
    result = defaultdict(list)
    main()
