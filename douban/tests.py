from collections import defaultdict

data = [{'tag': '虚构类书籍', 'title': 'OPUS 作品', 'url': 'https://book.douban.com/subject/30473909/', 'rate': 9.1, 'vote': 3064}, {'tag': '虚构类书籍', 'title': '你想活出怎样的人生', 'url': 'https://book.douban.com/subject/34659228/', 'rate': 8.9, 'vote': 1276}, {'tag': '虚构类书籍', 'title': '醉步男', 'url': 'https://book.douban.com/subject/30359030/', 'rate': 8.9, 'vote': 757}, {'tag': '虚构类书籍', 'title': '岛屿书', 'url': 'https://book.douban.com/subject/10537645/', 'rate': 8.4, 'vote': 802}, {'tag': '虚构类书籍', 'title': '消失的塞布丽娜', 'url': 'https://book.douban.com/subject/34448547/', 'rate': 8.4, 'vote': 345}, {'tag': '虚构类书籍', 'title': '网内人', 'url': 'https://book.douban.com/subject/34262174/', 'rate': 8.3, 'vote': 1935}, {'tag': '虚构类书籍', 'title': '春日序曲', 'url': 'https://book.douban.com/subject/33451948/', 'rate': 8.2, 'vote': 427}, {'tag': '虚构类书籍', 'title': '佛兰德镜子', 'url': 'https://book.douban.com/subject/34782362/', 'rate': 8.2, 'vote': 609}, {'tag': '虚构类书籍', 'title': '82年生的金智英', 'url': 'https://book.douban.com/subject/34434309/', 'rate': 7.9, 'vote': 6330}, {'tag': '虚构类书籍', 'title': '尸人庄谜案', 'url': 'https://book.douban.com/subject/30396712/', 'rate': 7.5, 'vote': 1646}, {'tag': '非虚构类书籍', 'title': '西方哲学史（第9版）', 'url': 'https://book.douban.com/subject/34447865/', 'rate': 9.5, 'vote': 146}, {'tag': '非虚构类书籍', 'title': '至高权力', 'url': 'https://book.douban.com/subject/30394978/', 'rate': 9.2, 'vote': 117}, {'tag': '非虚构类书籍', 'title': '书店日记', 'url': 'https://book.douban.com/subject/33459737/', 'rate': 8.8, 'vote': 454}, {'tag': '非虚构类书籍', 'title': '日本人为何选择了战争', 'url': 'https://book.douban.com/subject/34204669/', 'rate': 8.5, 'vote': 319}, {'tag': '非虚构类书籍', 'title': '设计之书', 'url': 'https://book.douban.com/subject/34661642/', 'rate': 8.5, 'vote': 144}, {'tag': '非虚构类书籍', 'title': '在别人的句子里', 'url': 'https://book.douban.com/subject/34441048/', 'rate': 8.4, 'vote': 848}, {'tag': '非虚构类书籍', 'title': '天才为何成群地来', 'url': 'https://book.douban.com/subject/33450028/', 'rate': 8.2, 'vote': 239}, {'tag': '非虚构类书籍', 'title': '李银河说爱情', 'url': 'https://book.douban.com/subject/34460345/', 'rate': 8.1, 'vote': 1013}, {'tag': '非虚构类书籍', 'title': '大脑健身房', 'url': 'https://book.douban.com/subject/34430051/', 'rate': 7.9, 'vote': 310}, {'tag': '非虚构类书籍', 'title': '焦虑型人格自救手册', 'url': 'https://book.douban.com/subject/34432245/', 'rate': 6.9, 'vote': 747}]


def convert_data_format(data):
    """
    [
        {'tag': tag, 'titles': ['xx', 'xx'], 'urls': ['xx', 'xx'], 'rates': ['xx', 'xx'], 'vote': ['xx', 'xx']},
        {...},
        {...},
    ]
    """
    result = []

    for data_obj in data:
        tmp = defaultdict(list)

        tmp[data_obj['tag']].append()

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
