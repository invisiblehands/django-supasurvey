import os

from django.test import TestCase

from supasurvey.utils import SchemaHandler


TESTDIR = os.path.dirname(__file__)


class SchemaHandlerTest(TestCase):
    def test_schemahandler(self):
        schema_handler = SchemaHandler()

        # currently reading from file
        # schema_handler.survey = survey
        # schema_handler.data = survey.data

        # replace data with this
        in_csv_pth = os.path.join(TESTDIR, 'data.csv')
        out_json_pth = os.path.join(TESTDIR, 'data.json')
        in_json_pth = os.path.join(TESTDIR, 'data.json')

        # read as csv and write to json
        schema_handler.read_lines(in_csv_pth)
        schema_handler.parse_as_dct()
        schema_handler.nest()
        schema_handler.write_json(out_json_pth, pretty=True)

        # read as json
        schema_handler.read_json(in_json_pth)
        schema_handler.to_python()

        # schema_handler.flatten()
        # schema_handler.nest()
