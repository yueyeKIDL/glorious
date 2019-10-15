# from django.core.cache import cache #引入缓存模块
# cache.set('v', '555', 60*60)      #写入key为v，值为555的缓存，有效期30分钟
# cache.has_key('v') #判断key为v是否存在
# cache.get('v')
from collections import defaultdict

d = {'美剧': [['美剧', '致命女人', 'https://movie.douban.com/subject/30401122/', '9.3', '118156'],
            ['美剧', '难以置信', 'https://movie.douban.com/subject/30122641/', '9.3', '20666']],
     '日剧': [['日剧', '凪的新生活', 'https://movie.douban.com/subject/33418567/', '8.9', '84462'],
            ['日剧', '孤独的美食家第八季', 'https://movie.douban.com/subject/34801559/', '9.4', '1555']]}
# for tag, title, url, rate, vote in d['美剧']:
#     print(tag, title, url, rate, vote)
L = ['tag', 'title', 'url','rate','vote']
tag, title, url, rate, vote = [list(i) for i in zip(*d['美剧'])]
print(tag, title, rate, vote)
