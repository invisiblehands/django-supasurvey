from decimal import Decimal
from collections import OrderedDict

from django.core.serializers import deserialize, serialize
from django.core.serializers.base import DeserializationError
from django.forms.util import ValidationError
from django.db import models
from django.test import TestCase
from django.core.exceptions import ValidationError

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from .fields import EmailField, ChooseYesNoField



class EmailFieldTest(TestCase):
    def test_normal_emailfield_no_data(self):
        """Test a normal emailfield behaviour"""
        
        data = {}
        files = []

        email = EmailField(label="What is your email address?", required=False)
        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(value, None)

        value = email.to_python(value)
        self.assertEqual(value, '')

        value = email.clean(value)
        self.assertEqual(value, '')


    def test_normal_emailfield_blank(self):
        """Test a normal emailfield behaviour with blank data"""
        
        
        data = {
            'email': ''
        }
        files = []

        email = EmailField(label="What is your email address?", required=False)
        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(value, '')

        value = email.to_python(value)
        self.assertEqual(value, '')

        value = email.clean(value)
        self.assertEqual(value, '')


    def test_normal_emailfield_bad_data(self):
        """Test a normal emailfield behaviour with bad data, should raise validationError"""
        
        stub = 'cody'
        data = {
            'email': stub
        }
        files = []

        email = EmailField(label="What is your email address?", required=False)
        value = email.widget.value_from_datadict(data, files, 'email')
        
        self.assertEqual(value, stub)
        self.assertRaises(ValidationError, email.clean, value)


    def test_normal_emailfield_good_data(self):
        """Test a normal emailfield behaviour with good data"""
        
        stub = 'cody@gmail.com'
        data = {
            'email': stub
        }
        files = []

        email = EmailField(label="What is your email address?", required=False)
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
            label="What is your email address?", 
            required=False,
            max_score=5)

        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(email.score(value), 0)


    def test_normal_emailfield_with_score_good(self):
        """Test a normal emailfield behaviour with good score and good data"""
        
        stub = 'cody@gmail.com'
        data = {
            'email': stub
        }
        files = []

        email = EmailField(
            label="What is your email address?", 
            required=False,
            max_score=5)

        value = email.widget.value_from_datadict(data, files, 'email')
        self.assertEqual(email.score(value), 5)


    def test_normal_emailfield_with_score_good_required(self):
        """Test a normal emailfield behaviour with good score and good data"""

        email = EmailField(
            label="What is your email address?", 
            required=True,
            max_score=5)

        self.assertEqual(email.score(''), 0)
        self.assertEqual(email.score('codydjango@gmail.com'), 5)



class YesNoFieldTest(TestCase):
    def test_yesno(self):
        """Test a normal yesnofield behaviour"""

        yesno = ChooseYesNoField(label="Are you a good dog?")

        self.assertEqual(yesno.clean('Yes'), 'Yes')
        self.assertEqual(yesno.score('Yes'), 0)
        self.assertEqual(yesno.score('No'), 0)


    def test_yesno_score(self):
        """Test a normal yesnofield behaviour"""

        yesno = ChooseYesNoField(label="Are you a good dog?", max_score=5, min_score=1)

        self.assertEqual(yesno.clean('Yes'), 'Yes')
        self.assertEqual(yesno.score('Yes'), 5)
        self.assertEqual(yesno.score('No'), 1)


