class ClassifyConverter:
    """自定义分类转换器"""
    regex = r'\w+|(\w+\+\w+)+'

    def to_python(self, value):
        """视图中接收的参数格式"""
        result = value.split('+')
        return result

    def to_url(self, value):
        """reverse反转后的url格式"""
        if isinstance(value, list):
            result = '+'.join(value)
            return result
        else:
            raise RuntimeError('参数不符合列表类型')


class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value
