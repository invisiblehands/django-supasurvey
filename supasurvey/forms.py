import floppyforms as forms, copy, decimal, autocomplete_light

from collections import OrderedDict
from decimal import *

from django.forms.formsets import BaseFormSet, formset_factory

from supasurvey.models import SurveyResponse
from supasurvey.fields import ChooseYesNoField, ChooseOneField, ChooseOneOpenField
from supasurvey.fields import ChooseMultipleField, ChooseOneForEachField
from supasurvey.fields import CharField, IntegerField, EmailField, TextField, SmallTextField, MultiFileField
from supasurvey.widgets import PlainTextWidget, PlainTextAreaWidget, PlainTextCheckboxWidget, PlainTextChooseOpenWidget



class VerifierForm(forms.Form):
    notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='Verifier Notes')

    score = forms.CharField(
        required=False,
        label='Verifier Score')


    def clean_score(self):
        THREEPLACES = Decimal(10) ** -3

        score = self.cleaned_data.get('score', None)
        if score:
            try:
                value = Decimal(score)
            except decimal.InvalidOperation, e:
                raise forms.ValidationError('Score must be in numeric form.')

            if value > self.max_score:
                raise forms.ValidationError('Score must be be less than maximum score of %s.' % self.max_score.quantize(THREEPLACES))

            if abs(value.as_tuple().exponent) > 3:
                raise forms.ValidationError('Scores must have no more than three decimal places.')

        return score


    def __init__(self, *args, **kwargs):
        self.max_score = kwargs.pop('max_score', Decimal(0))
        self.edit = kwargs.pop('edit', False)

        if self.max_score > 0:
            self.scoring = True
        else:
            self.scoring = False

        super(VerifierForm, self).__init__(*args, **kwargs)

        if self.edit == False:
            self.fields['notes'].widget = PlainTextAreaWidget()
            self.fields['score'].widget = PlainTextWidget()

        if self.scoring == False:
            del self.fields['score']




class SupaSurveyFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema', False)
        self.edit = kwargs.pop('edit', False)

        super(SupaSurveyFormSet, self).__init__(*args, **kwargs)

        for form in self.forms:
            form.empty_permitted = True


    def add_fields(self, form, index):
        super(SupaSurveyFormSet, self).add_fields(form, index)

        form.build(self.schema, self.edit)



class SupaSurveyForm(forms.Form):
    FIELDMAP = {
        'radio': ChooseOneField,
        'radio-open': ChooseOneOpenField,
        'radio-yes-no': ChooseYesNoField,
        'checkbox': ChooseMultipleField,
        'emailfield': EmailField,
        'textfield': SmallTextField,
        'textarea': TextField,
        'integerfield': CharField,
        'moneyfield': CharField,
        'file-multiple': MultiFileField
    }


    def __init__(self, *args, **kwargs):
        self._filesfields = []

        super(SupaSurveyForm, self).__init__(*args, **kwargs)


    def has_changed(self):
        """ this is required!  CR"""
        return True


    def _get_choices(self, answer_copy):
        answer_options_str = answer_copy.get('options', '')

        return answer_options_str.split('|')


    def _get_kwargs_for_type(self, answer_type, answer_copy):
        kwargs = {
            'label': answer_copy.get('label', None),
            'initial': answer_copy.get('initial', None),
            'required': answer_copy.get('required', False),
        }

        if answer_type in ['radio', 'radio-open', 'checkbox']:
            kwargs['choices'] = self._get_choices(answer_copy)

        if answer_type == 'file-multiple':
            kwargs['uploaded'] = []
            kwargs['label'] = 'Upload'
            kwargs['required'] = False

        return kwargs


    def add_field(self, answer_key, answer_type, answer_copy):
        answer_cls = self.FIELDMAP.get(answer_type, None)
        if answer_cls:
            kwargs = self._get_kwargs_for_type(answer_type, answer_copy)

            if answer_type == 'file-multiple':
                self._filesfields.append(answer_key)
                uploaded = self.initial.pop(answer_key, [])

                if not isinstance(uploaded, list):
                    uploaded = [uploaded]

                kwargs['uploaded'] = uploaded

            elif answer_type in ['radio', 'radio-yes-no']:
                answer_initial = self.initial.get(answer_key, None)
                if isinstance(answer_initial, list):
                    self.initial[answer_key] = answer_initial[0]

            elif answer_type == 'radio-open':
                answer_initial = self.initial.get(answer_key, None)
                if answer_initial and isinstance(answer_initial, list):
                    radio = answer_initial[0]
                    other = answer_initial[1]
                    answer_initial = other if other else radio
                    self.initial[answer_key] = answer_initial

            self.fields[answer_key] = answer_cls(**kwargs)

            if self.edit == False:
                field = self.fields[answer_key]

                if answer_type in ['textfield', 'textarea']:
                    field.widget = PlainTextAreaWidget()
                elif answer_type in ['file-multiple']:
                    field.label = 'Attached files'
                    field.widget = PlainTextWidget()
                elif answer_type in ['checkbox']:
                    field.widget = PlainTextCheckboxWidget()
                elif answer_type in ['radio', 'radio-open', 'radio-yes-no']:
                    field.widget = PlainTextChooseOpenWidget()
                else:
                    field.widget = PlainTextWidget()

                if hasattr(field, 'files'):
                    field.widget.files = field.files


        else:
            print 'no field class for %s' % answer_key


    def build(self, schema, edit):
        self._schema = schema
        self.edit = edit

        self.id = int(self._schema.get('id'))
        self.repeater = self._schema.get('repeater', False)
        self.answers = self._schema.get('answers')
        for answer_id, answer in self.answers.items():
            answer_copy = copy.deepcopy(answer)
            answer_type = answer_copy.pop('type')
            answer_key = 'questionset_%s__answer_%s' % (self.id, answer_id)
            self.add_field(answer_key, answer_type, answer_copy)


    def has_files(self):
        return True if self._filesfields else False


    def clean(self, *args, **kwargs):
        return super(SupaSurveyForm, self).clean(*args, **kwargs)



class SurveyResponseForm(autocomplete_light.ModelForm):
    class Meta:
        model = SurveyResponse
        exclude = ('survey', 'completion', 'total_score', 'data')


    def __init__(self, *args, **kwargs):
        super(SurveyResponseForm, self).__init__(*args, **kwargs)


