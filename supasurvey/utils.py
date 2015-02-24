import csv, os, codecs, collections, json, copy

from decimal import Decimal

from django.utils.html import conditional_escape
from django.conf import settings



def flatatt(attrs):
    """
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs.  It is assumed that the keys do not need
    to be XML-escaped.
    If the passed dictionary is empty, then return an empty string.
    If the value passed is None writes only the attribute (eg. required)
    """
    ret_arr = []
    for k, v in attrs.items():

        if v is None:
            ret_arr.append(u' %s' % k)
        else:
            ret_arr.append(u' %s="%s"' % (k, conditional_escape(v)))
    return u''.join(ret_arr)





# # http://stackoverflow.com/questions/1846135/python-csv-library-with-unicode-utf-8-support-that-just-works
class UnicodeCSVReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next()
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num



class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
        self.reader = UnicodeCSVReader(f, encoding=encoding, **kwds)




class SchemaHandler(object):
    """ This utility will read and write to a database or to a file the form schema.
    It will also be the utility that dynamically generates the django form from said
    schema.
    """

    def __init__(self, *args, **kwargs):
        self.levels = ['section', 'questionset', 'answer']

        super(SchemaHandler, self).__init__(*args, **kwargs)


    def read_lines(self, pth):
        with codecs.open(pth, 'r', 'utf-8') as f:
            self.input = f.readlines()


    def parse_as_dct(self):
        self.raw = UnicodeDictReader(self.input)


    def nest(self):
        self.data = collections.OrderedDict()
        data = self.data
        for row in self.raw:
            key = 'section'
            section_id = row.get('%s_id' % key)
            if not data.has_key(section_id):
                sectionset = {
                    'id': section_id,
                    'display': row.get('%s_display' % key),
                    'title': row.get('%s_title' % key),
                    'questionsets': collections.OrderedDict()
                }
                data[section_id] = sectionset


            key = 'questionset'
            questionsets = data[section_id]['questionsets']
            questionset_id = row.get('%s_id' % key)

            repeater_label = row.get('%s_repeater_label' % key, False)
            is_repeater = True if repeater_label else False

            if not questionsets.has_key(questionset_id):
                questionset = {
                    'id': questionset_id,
                    'title': row.get('%s_title' % key),
                    'description': row.get('%s_description' % key),
                    'repeater': is_repeater,
                    'repeater_label': repeater_label,
                    'answers': collections.OrderedDict()
                }

                dependencies = row.get('dependencies')
                if dependencies:
                    questionset['dependencies'] = dependencies

                questionsets[questionset_id] = questionset
                answer_id = 0


            key = 'answer'
            answers = data[section_id]['questionsets'][questionset_id]['answers']
            answer_id = answer_id + 1
            answer = {
                'id': answer_id,
            }

            answer_type = row.get('%s_type' % key)
            answer_label = row.get('%s_label' % key)
            answer_options = row.get('%s_options' % key)
            answer_minscore = row.get('%s_minscore' % key)
            answer_maxscore = row.get('%s_maxscore' % key)
            answer_scoring = row.get('%s_scoring' % key)
            answer_correct = row.get('%s_correct' % key)

            answer['label'] = answer_label

            if answer_type: answer['type'] = answer_type
            if answer_options: answer['options'] = answer_options
            if answer_minscore: answer['minscore'] = answer_minscore
            if answer_maxscore: answer['maxscore'] = answer_maxscore
            if answer_scoring: answer['scoring'] = answer_scoring
            if answer_correct: answer['correct'] = answer_correct

            answers[answer_id] = answer


    def flatten(self):
        data = self.data
        rows = []

        col = collections.OrderedDict()

        # first level (sections)
        for section_key, section in data.items():
            questionsets = section.pop('questionsets')

            for k, v in section.items():
                col['%s_%s' % ('section', k)] = v

            # next level (questionsets)
            for questionset_key, questionset in questionsets.items():
                answers = questionset.pop('answers')

                for kk, vv in questionset.items():
                    col['%s_%s' % ('questionset', kk)] = vv

                # next level (answers)
                for answer_key, answer in answers.items():
                    for kkk, vvv in answer.items():
                        col['%s_%s' % ('answer', kkk)] = vvv

                    rows.append(copy.deepcopy(col))

        self.raw = rows


    def export_json(self, pretty=False):
        if pretty:
            json_data = json.dumps(self.data, sort_keys=False, indent=4, separators=(',', ': '))
        else:
            json_data = json.dumps(self.data)

        return json_data


    def write_json(self, pth, pretty=False):
        with codecs.open(pth,'w','utf-8') as f:
            f.write(self.export_json(pretty))


    def read_json(self, pth):
        # http://stackoverflow.com/questions/6921699/can-i-get-json-to-load-into-an-ordereddict-in-python
        with codecs.open(pth,'r','utf-8') as f:
            self.json_raw = f.read()


    def to_python(self):
        self.data = json.loads(self.json_raw, object_pairs_hook=collections.OrderedDict)


    def get_questionsets(self, section_id):
        section_schema = self.get_section_schema(section_id)
        return copy.deepcopy(section_schema).get('questionsets')


    def get_section_schema(self, section_id):
        return self.data.get(unicode(section_id))



def get_schema_handler(survey):
    schema_handler = SchemaHandler()

    # currently reading from file
    # schema_handler.survey = survey
    # schema_handler.data = survey.data

    # replace data with this
    in_csv_pth = os.path.join(settings.PROJECT_ROOT, 'bin', 'par.csv')
    out_json_pth = os.path.join(settings.PROJECT_ROOT, 'bin', 'par_out.json')
    out_json_pth_processed = os.path.join(settings.PROJECT_ROOT, 'bin', 'par_out_processed.json')
    in_json_pth = os.path.join(settings.PROJECT_ROOT, 'bin', 'par_out.json')

    DEVELOPLMENT = getattr(settings, 'SUPASURVEY_DEVELOPMENT', True)
    if DEVELOPLMENT:
        schema_handler.read_lines(in_csv_pth)
        schema_handler.parse_as_dct()
        schema_handler.nest()
        schema_handler.data_bak1 = schema_handler.data
        schema_handler.write_json(out_json_pth, pretty=True)

    schema_handler.read_json(in_json_pth)
    schema_handler.to_python()
    # schema_handler.flatten()
    # schema_handler.nest()
    # schema_handler.data_bak2 = schema_handler.data
    # schema_handler.write_json(out_json_pth_processed, pretty=True)
    # assert schema_handler.data_bak1 == schema_handler.data_bak2

    # save updated data
    # survey.data = schema_handler.data
    # survey.save()

    return schema_handler
