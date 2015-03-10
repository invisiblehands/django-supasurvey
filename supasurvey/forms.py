import floppyforms as forms, copy

from decimal import *

from supasurvey.fields import ChooseYesNoField, ChooseOneField, ChooseOneOpenField
from supasurvey.fields import ChooseMultipleField, ChooseOneForEachField
from supasurvey.fields import CharField, IntegerField, EmailField, TextField



class SupaSurveyForm(forms.Form):
    FIELDMAP = {
        'radio': ChooseOneField,
        'radio-open': ChooseOneOpenField,
        'radio-yes-no': ChooseYesNoField,
        'checkbox': ChooseMultipleField,
        'textfield': CharField,
        'textarea': TextField,
        'integerfield': IntegerField,
        'emailfield': EmailField}


    def __init__(self, *args, **kwargs):
        self._max_score = Decimal(0);
        self._score = Decimal(0);
        self._schema = kwargs.pop('schema', False)

        super(SupaSurveyForm, self).__init__(*args, **kwargs)

        self.build()


    def get_score(self):
        if not self.is_bound:
            return 0

        self._max_score = Decimal(0);
        self._score = Decimal(0);
        self._calculate_score()

        return self._score


    def get_maxscore(self):
        self._calculate_maxscore();

        return self._max_score


    def _calculate_score(self):
        for name, field in self.fields.items():
            if hasattr(field, 'score'):
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
                self._score = sum([self._score, field.score(value)])


    def _calculate_maxscore(self):
        for name, field in self.fields.items():
            if hasattr(field, 'score'):
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
                self._max_score = sum([self._max_score, field.max_score])


    def _get_choices(self, answer_copy):
        answer_options_str = answer_copy.get('options', '')
        return answer_options_str.split('|')


    def _get_kwargs_for_type(self, answer_type, answer_copy):
        kwargs = {
            'label': answer_copy.get('label', None),
            'initial': answer_copy.get('initial', None),
            'required': answer_copy.get('required', False)
        }

        if answer_type in ['radio', 'radio-open', 'checkbox']:
            kwargs['choices'] = self._get_choices(answer_copy)

        return kwargs


    def add_field(self, answer_key, answer_type, answer_copy):
        answer_cls = self.FIELDMAP.get(answer_type, None)
        if answer_cls:
            kwargs = self._get_kwargs_for_type(answer_type, answer_copy)
            self.fields[answer_key] = answer_cls(**kwargs)


    def build(self, schema=None):
        if schema:
            self._schema = schema

        if not self._schema:
            return

        self.id = int(self._schema.get('id'))
        self.repeater = self._schema.get('repeater', False)
        self.answers = self._schema.get('answers')
        for answer_id, answer in self.answers.items():
            answer_copy = copy.deepcopy(answer)
            answer_type = answer_copy.pop('type')
            answer_key = 'questionset_%s__answer_%s' % (self.id, answer_id)
            self.add_field(answer_key, answer_type, answer_copy)
