import json

from decimal import *
from collections import OrderedDict

from django import forms
from django.forms.util import ValidationError
from django.forms.formsets import formset_factory
from django.core.exceptions import ValidationError
from django.test import TestCase

from supasurvey.forms import SupaSurveyForm
from supasurvey.fields import CharField, EmailField, MoneyField, ChooseYesNoField
from supasurvey.fields import ChooseOneField, ChooseOneOpenField, ChooseMultipleField







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
            3,4,5])


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
        self.assertEqual(len(formset), 3)


    def test_formset(self):
        FormClasses = [
            TestSupaSurveyQuestion1Form,
            TestSupaSurveyQuestion2Form,
            TestSupaSurveyQuestion3Form
        ]

        for question_id, FC in enumerate(FormClasses):
            formset = formset_factory(FC, extra=1)(prefix='question_%s' % question_id)
