from decimal import *
from collections import OrderedDict

from django.core.serializers import deserialize, serialize
from django.core.serializers.base import DeserializationError
from django.forms.util import ValidationError
from django.db import models
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django import forms

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from supasurvey.forms import SupaSurveyForm
from supasurvey.fields import CharField, EmailField, MoneyField, ChooseYesNoField, ChooseOneField, ChooseOneOpenField, ChooseMultipleField



class ScoreEmailFieldTest(TestCase):
    def test_normal_emailfield_no_data(self):
        """Test a normal emailfield behaviour"""
        
        data = {}
        files = []

        email = EmailField(label='What is your email address?', required=False)
        # find nothing called 'email' in datadict
        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(value, None)

        # cast to blank
        value = email.to_python(value)
        self.assertEqual(value, '')

        # still blank
        value = email.clean(value)
        self.assertEqual(value, '')


    def test_normal_emailfield_blank(self):
        """Test a normal emailfield behaviour with blank data"""
        
        
        data = {
            'email': ''
        }
        files = []

        email = EmailField(label='What is your email address?', required=False)
        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(value, '')

        value = email.to_python(value)
        self.assertEqual(value, '')

        value = email.clean(value)
        self.assertEqual(value, '')


    def test_normal_emailfield_bad_data(self):
        """Test a normal emailfield behaviour with bad data, should raise validationError"""
        
        data = {
            'email': 'cody'
        }
        files = []

        email = EmailField(label='What is your email address?', required=False)
        value = email.widget.value_from_datadict(data, files, 'email')
        
        self.assertEqual(value, data['email'])
        self.assertRaises(ValidationError, email.clean, value)


    def test_normal_emailfield_good_data(self):
        """Test a normal emailfield behaviour with good data"""
        
        stub = 'cody@gmail.com'
        data = {
            'email': stub
        }
        files = []

        email = EmailField(label='What is your email address?', required=False)
        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(value, stub)
        value = email.clean(value)
        self.assertEqual(value, stub)


    def test_normal_emailfield_with_score_bad(self):
        """Test a normal emailfield behaviour with score and bad data"""
        
        stub = 'cody'
        data = {
            'email': stub
        }
        files = []

        email = EmailField(
            label='What is your email address?', 
            required=False,
            max_score=5)


        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(email.score(value), 0)
        self.assertEqual(email.get_max_score(), 5)


    def test_normal_emailfield_with_score_good(self):
        """Test a normal emailfield behaviour with good score and good data"""
        
        stub = 'cody@gmail.com'
        data = {
            'email': stub
        }
        files = []

        email = EmailField(
            label='What is your email address?', 
            required=False,
            max_score=5)

        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(email.score(value), 5)


    def test_normal_emailfield_with_score_good_required(self):
        """Test a normal emailfield behaviour with good score and good data"""

        email = EmailField(
            label='What is your email address?', 
            required=True,
            max_score=5)

        self.assertEqual(email.score(''), 0)
        self.assertEqual(email.score('codydjango@gmail.com'), 5)


    def test_moneyfield(self):
        """Test a normal moneyfield behaviour"""

        email = MoneyField(
            label='How much money do you have?', 
            required=False,
            min_score=0,
            max_score=5)

        self.assertEqual(email.score(''), 0)
        self.assertEqual(email.score('10'), 5)
        self.assertEqual(email.score(''), 0)
        self.assertEqual(email.score('10.30'), 5)

        self.assertEqual(email.clean('10'), Decimal(10.00))
        self.assertEqual(email.clean('10'), Decimal(10))

        c = getcontext().copy()
        c.prec = 4
        self.assertEqual(email.clean('10.33'), c.create_decimal('10.33'))



class ScoreYesNoFieldTest(TestCase):
    def test_yesno_noscore(self):
        yesno = ChooseYesNoField(label='Are you a good dog?')

        self.assertEqual(yesno.clean('Yes'), 'Yes')
        self.assertEqual(yesno.score('Yes'), 0)
        self.assertEqual(yesno.score('No'), 0)


    def test_yesno_score(self):
        yesno = ChooseYesNoField(label='Are you a good dog?', max_score=5, min_score=1)

        self.assertEqual(yesno.clean('Yes'), 'Yes')
        self.assertEqual(yesno.score('Yes'), 5)
        self.assertEqual(yesno.score('No'), 1)


    def test_yesno_score_custom(self):
        yesno = ChooseYesNoField(
            label='Are you a good dog?', scores = [3,2])

        self.assertEqual(yesno.clean('Yes'), 'Yes')
        self.assertEqual(yesno.score('Yes'), 3)
        self.assertEqual(yesno.score('No'), 2)




class ScoreChooseOneFieldTest(TestCase):
    def test_chooseone_noscore(self):
        pick = ChooseOneField(
            label='Choose one', 
            choices = [
                '1-2 years',
                '3-5 years',
                '5-10 years'
            ],
        )

        self.assertEqual(pick.clean('1-2 years'), '1-2 years')
        self.assertEqual(pick.score('1-2 years'), 0)
        self.assertEqual(pick.score('5-10 years'), 0)


    def test_chooseone_score(self):
        pick = ChooseOneField(
            label='Choose one', 
            max_score=5, 
            min_score=1,
            choices = [
                '1-2 years',
                '3-5 years',
                '5-10 years'
            ],
        )

        self.assertEqual(pick.clean(''), '')
        self.assertEqual(pick.score(''), 1)

        self.assertEqual(pick.clean('1-2 years'), '1-2 years')
        self.assertEqual(pick.score('1-2 years'), 5)


    def test_chooseone_score_map(self):
        pick = ChooseOneField(
            label='Choose one', 
            choices = [
                '1-2 years',
                '3-5 years',
                '5-10 years'
            ],
            scores = [
                2,
                3,
                4
            ]
        )

        self.assertEqual(pick.clean(''), '')
        self.assertEqual(pick.score(''), 0)

        self.assertEqual(pick.clean('1-2 years'), '1-2 years')
        self.assertEqual(pick.score('1-2 years'), 2)
        self.assertEqual(pick.score('3-5 years'), 3)
        self.assertEqual(pick.score('5-10 years'), 4)


    def test_chooseoneopen_noscore(self):
        choose = ChooseOneOpenField(
            label='How did you first hear about being a good dog?', 
            choices=[
                'A friend/family member told me about it',
                'I heard about it online',
                'I saw it at a bookstore',
                'I found it at a library',
                'I received an offer in the mail',
                'I have a copy in my office']
        )

        self.assertEqual(choose.clean(''), '')
        self.assertEqual(choose.score(''), 0)

        self.assertEqual(choose.clean('A friend/family member told me about it'), 'A friend/family member told me about it')
        self.assertEqual(choose.score('A friend/family member told me about it'), 0)
        self.assertEqual(choose.score('custom value'), 0)


    def test_chooseoneopen_score(self):
        choose = ChooseOneOpenField(
            label='How did you first hear about being a good dog?', 
            choices=[
                'A friend/family member told me about it',
                'I heard about it online',
                'I saw it at a bookstore',
                'I found it at a library',
                'I received an offer in the mail',
                'I have a copy in my office'],
            scores=[20,21,22,31,32,41,11]
        )

        self.assertEqual(choose.clean(''), '')
        self.assertEqual(choose.score(''), 0)

        self.assertEqual(choose.clean('A friend/family member told me about it'), 'A friend/family member told me about it')
        self.assertEqual(choose.score('A friend/family member told me about it'), 20)
        self.assertEqual(choose.score('custom value'), 11)


    def test_choosemultiple_score(self):
        choose = ChooseMultipleField(
            label='How did you first hear about being a good dog?', 
            choices=[
                'A friend/family member told me about it',
                'I heard about it online',
                'I saw it at a bookstore',
                'I found it at a library',
                'I received an offer in the mail',
                'I have a copy in my office'],
            scores=['3','3','3','4','4','5']
        )

        self.assertEqual(choose.clean([]), [])
        self.assertEqual(choose.score([]), 0)
        self.assertEqual(choose.score(['A friend/family member told me about it']), 3)
        self.assertEqual(choose.score(
            [
                'A friend/family member told me about it',
                'I heard about it online'
            ]
        ), 6)


    def test_choosemultiple_score_decimal(self):
        choose = ChooseMultipleField(
            label='How did you first hear about being a good dog?', 
            choices=[
                'A friend/family member told me about it',
                'I heard about it online',
                'I saw it at a bookstore',
            ],
            scores=['1.1','2.2','3.3']
        )

        self.assertEqual(choose.score(
            [
                'A friend/family member told me about it',
                'I heard about it online'
            ]
        ), Decimal('3.3'))





class TestSupaSurveyForm(SupaSurveyForm):
    name = CharField(
        label="What is your name?",
        min_score=0,
        max_score=2)
    
    email = EmailField(
        label="What is your email address?",
        min_score=0,
        max_score=2)

    yes_no = ChooseYesNoField(
        label="Are you a good dog?", 
        min_score=0,
        max_score=10)

    choose_one = ChooseOneField(
        label="If yes, how long have you been a good dog?", 
        choices = [
            "1-2 years",
            "3-5 years",
            "5-10 years"],
        scores = [
            3,4,5
        ])



class ScoreYesNoFieldTest(TestCase):
    def test_form_nopost_noscore(self):
        form = SupaSurveyForm()
        self.assertFalse(form.is_valid())

    def test_form_unbound_score(self):
        form = SupaSurveyForm()
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_score(), 0)

    def test_form_bound_blank_score(self):
        data = {}
        form = SupaSurveyForm(data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.get_score(), 0)

    def test_form_bound_data_not_valid(self):
        data = {
            'email': 'codydjango@gmail.com',
            'yes_no': 'Yes',
            'choose_one': '3-5 years'
        }

        form = TestSupaSurveyForm(data)
        self.assertEquals(form.get_maxscore(), 19)
        self.assertEquals(form.get_score(), 16)

    def test_form_bound_data_valid(self):
        data = {
            'email': 'codydjango@gmail.com',
            'yes_no': 'Yes',
            'choose_one': '3-5 years'
        }

        form = TestSupaSurveyForm(data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.get_maxscore(), 19)
        self.assertEquals(form.get_score(), 16)






class TestFormRegular(forms.Form):
    title = forms.CharField()
    pub_date = forms.DateField()
    label = CharField(
        label='What is your profession?',
        min_score=0,
        max_score=2)


class TestFormSupa(SupaSurveyForm):
    title = forms.CharField()
    pub_date = forms.DateField()
    label = CharField(
        label='What is your profession?',
        min_score=0,
        max_score=2)



class TestSupaSurveyQuestion1Form(SupaSurveyForm):
    name = CharField(
        label="What is your name?",
        min_score=0,
        max_score=2)
    
    email = EmailField(
        label="What is your email address?",
        min_score=0,
        max_score=2)



class TestSupaSurveyQuestion2Form(SupaSurveyForm):
    label = CharField(
        label="What is your profession?",
        min_score=0,
        max_score=2)
    
    yes_no = ChooseYesNoField(
        label="Are you a good dog?", 
        min_score=0,
        max_score=10)


class TestSupaSurveyQuestion3Form(SupaSurveyForm):
    choose_one = ChooseOneField(
    label="If yes, how long have you been a good dog?", 
    choices = [
        "1-2 years",
        "3-5 years",
        "5-10 years"],
    scores = [
        3,4,5
    ])




class FormSetTest(TestCase):
    def test_1(self):
        formset = formset_factory(TestFormSupa, extra=3)()
        # for count, form in enumerate(formset):
        #     print count, form.as_table()
        self.assertEqual(len(formset), 3)


    def test_formset(self):
        # https://docs.djangoproject.com/en/dev/topics/forms/formsets/#using-more-than-one-formset-in-a-view
        # http://yergler.net/blog/2009/09/27/nested-formsets-with-django/
        FormClasses = [
            TestSupaSurveyQuestion1Form,
            TestSupaSurveyQuestion2Form,
            TestSupaSurveyQuestion3Form
        ]

        for question_id, FC in enumerate(FormClasses):
            formset = formset_factory(FC, extra=1)(prefix='question_%s' % question_id)

            for count, form in enumerate(formset):
                print count, form.as_table()







