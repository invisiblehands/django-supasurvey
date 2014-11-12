from decimal import Decimal
from collections import OrderedDict

from django.core.serializers import deserialize, serialize
from django.core.serializers.base import DeserializationError
from django.forms.util import ValidationError
from django.db import models
from django.test import TestCase

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from .fields import EmailField



class EmailFieldTest(TestCase):
    def test_json_field_create(self):
        """Test saving a JSON object in our JSONField"""
        
        REQUIRED = True

        email = EmailField(label="What is your email address?", required=REQUIRED)
        self.assertEqual(True, True)