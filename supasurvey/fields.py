import floppyforms as forms

from django.core.exceptions import ValidationError

from .widgets import RadioSelectOpen, RadioSelectOptions
from .widgets import ChooseOneForEach, ChooseOneForSubject



class EmailField(forms.EmailField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)

    def get_csv_value(self, v):
        return v
        
    def get_formatted_value(self, v):
        return v



class ChooseYesNoField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        choices = (("Y", "Yes"), ("N", "No"))

        widget = RadioSelectOptions(
            stacked=False,
            required=required)

        kwargs.update({
            "label": args[0],
            "choices": choices,
            "widget": widget,
            "required": required
        })

        super(ChooseYesNoField, self).__init__(**kwargs)

    def get_csv_value(self, v):
        return v

    def get_formatted_value(self, v):
        return v


class ChooseOneField(forms.ChoiceField):
    def __init__(self, label, choices, *args, **kwargs):
        required = kwargs.pop('required', False)
        stacked = kwargs.pop("stacked", None)
        choices = tuple([(x, x) for x in choices])
        widget = kwargs.pop("widget", None)

        if widget == None:
            widget = RadioSelectOptions(
                stacked=stacked,
                required=required)
        
        kwargs.update({
            "label": label,
            "widget": widget,
            "choices": choices,
            "required": required
        })
        
        super(ChooseOneField, self).__init__(**kwargs)

    def get_csv_value(self, v):
        return v

    def get_formatted_value(self, v):
        return v


class ChooseOneOpenField(forms.ChoiceField):
    def __init__(self, label, choices, *args, **kwargs):
        required = kwargs.pop('required', False)

        choices = [(x, x) for x in choices]
        choices.append(('other', 'Other'))
        choices = tuple(choices)
        
        widget = RadioSelectOpen(
            stacked=True,
            required=required)

        kwargs.update({
            "label": label,
            "choices": choices,
            "widget": widget,
            "required": required
        })

        super(ChooseOneOpenField, self).__init__(**kwargs)

    def get_csv_value(self, v):
        return v

    def get_formatted_value(self, v):
        return v


    def clean(self, value, *args, **kwargs):
        if value == "Other":
            raise ValidationError('Please specify.', code='invalid')
        return super(ChooseOneOpenField, self).clean(value, *args, **kwargs)

    def valid_value(self, value):
        if value:
            return True
        return False


class ChooseMultipleField(forms.MultipleChoiceField):
    def __init__(self, label, choices, *args, **kwargs):
        required = kwargs.pop('required', False)
        choices = [(x, x) for x in choices]
        widget = forms.CheckboxSelectMultiple
        kwargs.update({
            "label": label,
            "widget": widget,
            "choices": tuple(choices),
            "required": required
        })
        
        super(ChooseMultipleField, self).__init__(**kwargs)

    def get_csv_value(self, v):
        return v

    def get_formatted_value(self, v):
        html = '<ul style="padding-left: 1em;">'
        for x in v:
            html += '<li style="list-style-type: disc; list-style-position:outside; width: 160px;">%s</li>' % x
        html += "</ul>"
        return html


class OpenField(forms.CharField):
    def __init__(self, label, *args, **kwargs):
        required = kwargs.pop('required', False)
        widget = forms.Textarea

        kwargs.update({
            "label": label,
            "widget": widget,
            "required": required
        })

        super(OpenField, self).__init__(**kwargs)


    def get_csv_value(self, v):
        return v

    def get_formatted_value(self, v):
        return v


class ChooseOneForEachField(forms.MultiValueField):
    def __init__(self, label, choices=[], subjects=[], stacked=False, *args, **kwargs):
        required = kwargs.pop('required', False)
        error_messages = {
            'required': 'These fields are required.'
        }

        fields = tuple([ChooseOneField(subject, choices, widget=ChooseOneForSubject(subject, stacked=stacked, required=required)) for subject in subjects])
        widget = ChooseOneForEach(widgets=tuple([field.widget for field in fields]))
        self.num_fields = len(fields)

        kwargs = {
            "label": label,
            "fields": fields, 
            "widget": widget,
            "required": required,
            "error_messages": error_messages, 
        }

        super(ChooseOneForEachField, self).__init__(*args, **kwargs)


    def get_csv_value(self, v):
        subjects = [f.widget.subject for f in self.fields]
        values = v.split('|')
        zipped = zip(subjects, values)
        txt = ""
        for x, y in zipped:
            txt += "[%s:%s]" %(x, y)

        return txt


    def get_formatted_value(self, v):
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