from django import template

register = template.Library()


# 注册方式一：装饰器注册
@register.filter(name='joint')
def my_joint(value, other):
    """
    自定义过滤器函数
    模板使用样式 -> value|joint:other
    """
    return value + other


# 注册方式二：常规注册
register.filter('joint', my_joint)


from datetime import datetime