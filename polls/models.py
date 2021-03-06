import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(verbose_name='内容', max_length=200)
    pub_date = models.DateTimeField('发布日期', auto_now_add=True)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = '近期发布'

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = verbose_name_plural = '问卷'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
