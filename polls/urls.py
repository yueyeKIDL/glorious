from django.urls import path, register_converter

from polls import views
from polls.converters import ClassifyConverter

app_name = 'polls'

# 注册转换器
register_converter(ClassifyConverter, 'clss')

urlpatterns = [
    path('', views.index, name='index'),
    path('question_first/', views.question_first, name='question_first'),
    path('choice_first/', views.choice_first, name='choice_first'),
    path('book/<clss:classify>/', views.book_classify, name='book_classify'),
]
