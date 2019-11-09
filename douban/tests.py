from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

d = {'name':'yueyeKIDL'}
print(d.setdefault('name1', 'xiaoyue'))
print(d)