import floppyforms as forms

from django import forms as django_forms
from django.utils.html import mark_safe
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

NONEVALUE = 'None'

class RadioSelectWidget(forms.RadioSelect):
    template_name = 'floppyforms/radio.html'


    def __init__(self, *args, **kwargs):
        self.is_required = kwargs.pop('required', False)

        super(RadioSelectWidget, self).__init__(*args, **kwargs)


    def get_context(self, name, value, attrs):
        ctx = super(RadioSelectWidget, self).get_context(name, value, attrs)

        ctx['required'] = self.is_required
        return ctx




class PlainTextWidget(forms.Widget):
    def render(self, name, value, *args, **kwargs):
        value = value if value else NONEVALUE

        if hasattr(self, 'files'):
            if self.files:
                files = ['<li><a href="%s">%s</a></li>' % (f[1].get_absolute_url(), f[1].basename) for f in self.files]
                value = """
                    <ul>
                        %s
                    </ul>
                """ % ''.join(files)
            else:
                value = '<span class="no-files">No uploaded files.</span>'

        return mark_safe(value)



class PlainTextChooseOpenWidget(forms.Widget):
    def render(self, name, value, *args, **kwargs):
        if value and len(value) == 2:
            val1 = value[0]
            if val1.lower() == 'other':
                value = value[1]
            else:
                value = value[0]

        return mark_safe(value)


class PlainTextCheckboxWidget(forms.Widget):
    def render(self, name, value, *args, **kwargs):
        value = value if value else []
        value = ', '.join(value)
        return mark_safe(value)



class PlainTextAreaWidget(forms.Widget):
    def render(self, name, value, *args, **kwargs):

        value = value if value else NONEVALUE
        value = """<pre>%s</pre>""" % value

        if hasattr(self, 'files'):
            if self.files:
                files = ['<li><a href="%s">%s</a></li>' % (f[1].get_absolute_url(), f[1].basename) for f in self.files]
                value += """
                    <ul>
                        %s
                    </ul>
                """ % ''.join(files)
            else:
                value += '<span class="no-files">No uploaded files.</span>'

        return mark_safe(value)




class RadioSelectOpenWidget(RadioSelectWidget):
    template_name = 'floppyforms/radio-open.html'



class RadioSelectOpenRenderer(django_forms.RadioSelect.renderer):
    def __init__(self, *args, **kwargs):
        super(RadioSelectOpenRenderer, self).__init__(*args, **kwargs)

        self.choices, self.other = self.choices[:-1], self.choices[-1]


    def __iter__(self):
        for input in super(RadioSelectOpenRenderer, self).__iter__():
            yield input

        sid = '%s_%s' % (self.attrs['id'], self.other[0]) if 'id' in self.attrs else ''
        label_for = ' for="%s"' % sid if sid else ''
        checked = '' if not force_unicode(self.other[0]) == self.value else 'checked="true" '

        inter = '<label%s><input type="radio" id="%s" value="%s" name="%s" %s />%s</label> %%s'
        # mark_safe(inter)
        polated = inter % (label_for, sid, self.other[0], self.name, checked, self.other[1])

        yield mark_safe(polated)



class RadioSelectOpenMultiWidget(forms.MultiWidget):
    def __init__(self, widgets, choices, attrs=None):
        self.choices = choices
        self.other = 'Other'

        super(RadioSelectOpenMultiWidget, self).__init__(widgets, attrs)


    def decompress(self, value):
        if not value:
            return [None, None]

        if value in dict(self.choices).keys():
            return [value, '']
        else:
            return [self.other, value]


    def render(self, name, value, *args, **kwargs):
        return super (RadioSelectOpenMultiWidget, self).render(name, value, *args, **kwargs)


    def format_output(self, rendered_widgets):
        return rendered_widgets[0] % rendered_widgets[1]



class ChooseOneForSubject(forms.RadioSelect):
    template_name = 'floppyforms/choose-one-for-subject.html'

    def __init__(self, subject, *args, **kwargs):
        self.subject = subject
        self.is_required = kwargs.pop('required', False)

        super(ChooseOneForSubject, self).__init__(*args, **kwargs)


    def get_context(self, name, value, attrs):
        ctx = super(ChooseOneForSubject, self).get_context(name, value, attrs)
        ctx['required'] = True # is_required is getting overwritten somewhere.
        ctx['subject'] = self.subject
        return ctx



class ChooseOneForEach(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        self.num_widgets = len(kwargs['widgets'])

        super(ChooseOneForEach, self).__init__(*args, **kwargs)


    def decompress(self, value):
        if value:
            return value.split('|')

        return [None for x in range(1,self.num_widgets)]
