from django.contrib import admin

from polls.models import Question


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    fields = ['question_text', 'pub_date']
    list_filter = ['pub_date']


admin.site.register(Question, QuestionAdmin)
