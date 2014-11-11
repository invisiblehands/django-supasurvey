from django.utils.html import conditional_escape


def flatatt(attrs):
    """
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs.  It is assumed that the keys do not need
    to be XML-escaped.
    If the passed dictionary is empty, then return an empty string.
    If the value passed is None writes only the attribute (eg. required)
    """
    ret_arr = []
    for k, v in attrs.items():

        if v is None:
            ret_arr.append(u' %s' % k)
        else:
            ret_arr.append(u' %s="%s"' % (k, conditional_escape(v)))
    return u''.join(ret_arr)


class SurveyBuilder(object):
    """ This utility will read and write to a database or to a file the form schema.
    It will also be the utility that dynamically generates the django form from said
    schema.
    """
    pass