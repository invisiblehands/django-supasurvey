import floppyforms as forms

from django.core.exceptions import ValidationError

from .widgets import RadioSelectOpen, RadioSelectOptions
from .widgets import ChooseOneForEach, ChooseOneForSubject



class ScoreFormFieldBase(object):
    def __init__(self, *args, **kwargs):
        self.min_score = kwargs.pop('min_score', 0)
        self.max_score = kwargs.pop('max_score', 0)
        self.correct = kwargs.pop('correct', None)
        self.scores = kwargs.pop('scores', [])
        self._score = self.min_score

        super(ScoreFormFieldBase, self).__init__(*args, **kwargs)


    def score(self, v):
        try:
            self.clean(v)
        except ValidationError, e:
            pass
        return self._score
    

    def clean(self, value):
        self._score = self.min_score

        try:
            cleaned = super(ScoreFormFieldBase, self).clean(value);
            self._score = self.max_score

            if self.correct:
                self._score = self.max_score if cleaned == self.correct else self.min_score
            else:
                self._score = self.max_score
        except ValidationError, e:
            raise
        return cleaned



class OutputFormatFieldBase(object):
    def get_csv_value(self, v):
        return v
        
    def get_formatted_value(self, v):
        return v



class CharField(OutputFormatFieldBase, ScoreFormFieldBase, forms.CharField):
    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        min_length = kwargs.pop('min_length', None)
        max_length = kwargs.pop('max_length', None)
        widget = forms.TextInput

        kwargs.update({
            'widget': widget,
            'required': required,
            'max_length': max_length,
            'min_length': min_length
        })

        super(CharField, self).__init__(**kwargs)



class TextField(OutputFormatFieldBase, ScoreFormFieldBase, forms.CharField):
    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        min_length = kwargs.pop('min_length', None)
        max_length = kwargs.pop('max_length', None)
        widget = forms.Textarea

        kwargs.update({
            'widget': widget,
            'required': required,
            'max_length': max_length,
            'min_length': min_length,
        })

        super(TextField, self).__init__(**kwargs)



class EmailField(OutputFormatFieldBase, ScoreFormFieldBase, forms.EmailField):
    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)

        kwargs.update({
            'required': required
        })
        
        super(EmailField, self).__init__(*args, **kwargs)



class ChooseYesNoField(OutputFormatFieldBase, ScoreFormFieldBase, forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        correct = kwargs.pop('correct', 'Yes')
        choices = ['Yes', 'No']
        choices = tuple([(x, x) for x in choices])

        widget = RadioSelectOptions(
            stacked=False,
            required=required)

        kwargs.update({
            'choices': choices,
            'widget': widget,
            'required': required,
            'correct': correct
        })

        super(ChooseYesNoField, self).__init__(**kwargs)


class ChooseOneField(OutputFormatFieldBase, ScoreFormFieldBase, forms.ChoiceField):
    def __init__(self, choices, *args, **kwargs):
        required = kwargs.pop('required', False)
        stacked = kwargs.pop('stacked', None)
        choices = kwargs.pop('choices', [])
        choices = tuple([(x, x) for x in choices])
        widget = kwargs.pop('widget', None)

        if widget == None:
            widget = RadioSelectOptions(
                stacked=stacked,
                required=required)
        
        kwargs.update({
            'widget': widget,
            'choices': choices,
            'required': required
        })
        
        super(ChooseOneField, self).__init__(**kwargs)



class ChooseOneOpenField(OutputFormatFieldBase, ScoreFormFieldBase, forms.ChoiceField):
    def __init__(self, choices, *args, **kwargs):
        required = kwargs.pop('required', False)

        choices = [(x, x) for x in choices]
        choices.append(('other', 'Other'))
        choices = tuple(choices)
        
        widget = RadioSelectOpen(
            stacked=True,
            required=required)

        kwargs.update({
            'choices': choices,
            'widget': widget,
            'required': required
        })

        super(ChooseOneOpenField, self).__init__(**kwargs)

    def clean(self, value, *args, **kwargs):
        if value == 'Other':
            raise ValidationError('Please specify.', code='invalid')
        return super(ChooseOneOpenField, self).clean(value, *args, **kwargs)

    def valid_value(self, value):
        if value:
            return True
        return False



class ChooseMultipleField(OutputFormatFieldBase, ScoreFormFieldBase, forms.MultipleChoiceField):
    def __init__(self, choices, *args, **kwargs):
        required = kwargs.pop('required', False)
        choices = [(x, x) for x in choices]
        widget = forms.CheckboxSelectMultiple
        kwargs.update({
            'widget': widget,
            'choices': tuple(choices),
            'required': required
        })
        
        super(ChooseMultipleField, self).__init__(**kwargs)

    def get_formatted_value(self, v):
        """ Override this function to display an html list. """
        html = '<ul style="padding-left: 1em;">'
        for x in v:
            html += '<li style="list-style-type: disc; list-style-position:outside; width: 160px;">%s</li>' % x
        html += "</ul>"
        return html



class ChooseOneForEachField(ScoreFormFieldBase, forms.MultiValueField):
    def __init__(self, choices=[], subjects=[], stacked=False, *args, **kwargs):
        required = kwargs.pop('required', False)
        error_messages = {
            'required': 'These fields are required.'
        }

        fields = tuple([ChooseOneField(subject, choices, widget=ChooseOneForSubject(subject, stacked=stacked, required=required)) for subject in subjects])
        widget = ChooseOneForEach(widgets=tuple([field.widget for field in fields]))
        self.num_fields = len(fields)

        kwargs = {
            'fields': fields, 
            'widget': widget,
            'required': required,
            'error_messages': error_messages, 
        }

        super(ChooseOneForEachField, self).__init__(*args, **kwargs)

    def get_csv_value(self, v):
        """ the subject/choice is represented as a key-value pair and is rendered in the
        csv output file as a string in the format of "[subject:choice],[subject:choice]..."
        """
        subjects = [f.widget.subject for f in self.fields]
        values = v.split('|')
        zipped = zip(subjects, values)
        txt = ""
        for x, y in zipped:
            txt += "[%s:%s]" %(x, y)

        return txt

    def get_formatted_value(self, v):
        """ the subject/choice is represented as a key-value pair and is rendered in the
        admin as a html list.
        """
        subjects = [f.widget.subject for f in self.fields]
        values = v.split('|')
        zipped = zip(subjects, values)
        html = '<ul style="padding-left: 1em;">'
        for x, y in zipped:
            html += '<li style="list-style-type: disc; list-style-position:outside; width: 160px;">%s: %s</li>' % (x, y)
        html += "</ul>"

        return html


    def to_python(self, value):
        super(ChooseOneForEachField, self).to_python(*args, **kwargs)


    def get_prep_value(self, value):
        super(ChooseOneForEachField, self).get_prep_value(*args, **kwargs)


    def get_db_prep_value(self, value):
        super(ChooseOneForEachField, self).get_db_prep_value(*args, **kwargs)


    def compress(self, data_list):
        if data_list:
            return "|".join(data_list)

        return [None for x in range(1, self.num_fields)]