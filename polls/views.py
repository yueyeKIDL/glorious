from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import reverse
from django.urls import reverse

from polls.models import Choice, Question


# def create_permission(request):
#     content_type = ContentType.objects.get_for_model(Choice)
#     Permission.objects.create(codename='yueyeKIDL', name='VIP特权', content_type=content_type)
#     return HttpResponse('添加特权成功！')


def create_permission(request):
    # user = User.objects.first()
    # print(111,user)
    # content_type = ContentType.objects.get_for_model(Choice)
    # permissions = Permission.objects.filter(content_type=content_type)
    # for permission in permissions:
    #     any([23,4])
    #     user.user_permissions.add()
    return HttpResponse('ok')


def book_classify(request, classify):
    book_msg = '书籍分类为{}'.format(classify)
    return HttpResponse(book_msg)


def book_year(request, year):
    book_msg = '书籍出版日期为{}'.format(year)
    print(type(book_msg))
    reverse_url = reverse('polls:book_year', kwargs={'year': year})
    return HttpResponse(book_msg)


def index(request):
    context = {
        'name': 'yueyeKIDL'
    }
    return render(request, 'index.html', context=context)


def question_first(request):
    question = Question.objects.create(question_text='每天充满活力？')
    Choice.objects.create(question=question, choice_text='元气满满')
    Choice.objects.create(question=question, choice_text='浑身乏力')
    return HttpResponse('ok')


def choice_first(request):
    choice1 = Choice(choice_text='大神')
    choice2 = Choice(choice_text='小白')
    question = Question.objects.create(question_text='你的水准？')
    question.choice_set.add(choice1, choice2, bulk=False)
    return HttpResponse('ok')
