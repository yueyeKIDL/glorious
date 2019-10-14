# from django.core.cache import cache #引入缓存模块
# cache.set('v', '555', 60*60)      #写入key为v，值为555的缓存，有效期30分钟
# cache.has_key('v') #判断key为v是否存在
# cache.get('v')



d = {'a':1}
print(d.setdefault('a1',2))
print(d)