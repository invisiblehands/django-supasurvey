import csv, os, codecs, collections, pprint, json, copy

from django.utils.html import conditional_escape
from django.conf import settings
from django.forms.formsets import BaseFormSet, formset_factory
from django import forms

from supasurvey.forms import SupaSurveyForm

pp = pprint.PrettyPrinter(depth=6)



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




class SupaSurveyFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self._schema = kwargs.pop('schema', None)
        super(SupaSurveyFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True

    def add_fields(self, form, index):
        super(SupaSurveyFormSet, self).add_fields(form, index)
        form.build(self._schema)




class FormBuilder(object):
    """ takes list of questionset schemas and puts out a list of augmented formsets 
    to be used in the templates or with a templatetag."""

    def __init__(self, *args, **kwargs):
        super(FormBuilder, self).__init__(*args, **kwargs)


    def create_form(self, questionset_schema):
        return SupaSurveyForm(schema=questionset_schema)


    def create_formset(self, questionset_schema, prefix, POST=None, FILES=None):
        qss = questionset_schema
        FormSet = formset_factory(SupaSurveyForm, extra=1, formset=SupaSurveyFormSet)
        formset = FormSet(POST, FILES, prefix=prefix, schema=qss)

        if hasattr(formset, 'meta'):
            raise Exception ('has meta')

        formset.meta = {
            'id': qss.get('id', False),
            'title': qss.get('title', False),
            'description': qss.get('description', False),
            'repeater': qss.get('repeater', False)
        }

        return formset


    def get_prefix(self, questionset_id):
        return 'questionset_%s' % questionset_id


    def get_formsets(self, schemas, POST=None, FILES=None):
        formsets = []

        if not schemas:
            raise Exception('no schema provided.')

        questionsets = copy.deepcopy(schemas).get('questionsets')

        for questionset_id, questionset_schema in questionsets.items():
            prefix = self.get_prefix(questionset_id)
            formset = self.create_formset(
                    questionset_schema=questionset_schema, 
                    prefix=prefix, 
                    POST=POST, 
                    FILES=None)
            formsets.append(formset)
            # print 'completed questionset', questionset_id

        return formsets







# # http://stackoverflow.com/questions/1846135/python-csv-library-with-unicode-utf-8-support-that-just-works
class UnicodeCsvReader(object):
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
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)




class SchemaHandler(object):
    """ This utility will read and write to a database or to a file the form schema.
    It will also be the utility that dynamically generates the django form from said
    schema.
    """

    def __init__(self, *args, **kwargs):
        self.levels = ['section', 'questionset', 'answer']
        self.builder = FormBuilder()

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
            if not questionsets.has_key(questionset_id):
                questionset = {
                    'id': questionset_id,
                    'title': row.get('%s_title' % key),
                    'description': row.get('%s_description' % key),
                    'repeater': row.get('%s_repeater' % key),
                    'answers': collections.OrderedDict()
                }
                questionsets[questionset_id] = questionset
                answer_id = 0


            key = 'answer'
            answers = data[section_id]['questionsets'][questionset_id]['answers']
            answer_id = answer_id + 1
            answer = {
                'id': answer_id,
                'type': row.get('%s_type' % key),
                'label': row.get('%s_label' % key),
                'options': row.get('%s_options' % key),
                'maxscore': row.get('%s_maxscore' % key),
                'scoring': row.get('%s_scoring' % key),
                'correct': row.get('%s_correct' % key)
            }
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


    def get_all_answer_types(self):
        if self.raw:
            lst = [col.get('answer_type') for col in self.raw]
            lst = list(set(lst))
            return lst
        return []


    def get_section(self, num=None, POST=None, FILES=None):
        if num:
            self.set_section(num)

        section = self.data.get(self._section_id)

        return {
            'display': section.get('display'),
            'title': section.get('title'),
            'formsets': self.get_formsets(POST, FILES)
        }

    def set_section(self, num):
        self._section_id = unicode(num)


    def get_formsets(self, POST=None, FILES=None):
        section_schema = self.data.get(self._section_id)

        return self.builder.get_formsets(section_schema, POST, FILES)






def get_schema_handler():
    schema_handler = SchemaHandler()
    
    in_csv_pth = os.path.join(settings.PROJECT_ROOT, 'bin', 'par.csv')
    out_json_pth = os.path.join(settings.PROJECT_ROOT, 'bin', 'par_out.json')
    out_json_pth_processed = os.path.join(settings.PROJECT_ROOT, 'bin', 'par_out_processed.json')
    in_json_pth = os.path.join(settings.PROJECT_ROOT, 'bin', 'par_out.json')
    
    schema_handler.read_lines(in_csv_pth)
    schema_handler.parse_as_dct()
    schema_handler.nest()
    schema_handler.data_bak1 = schema_handler.data
    schema_handler.write_json(out_json_pth, pretty=True)
    schema_handler.read_json(in_json_pth)
    schema_handler.to_python()
    schema_handler.flatten()
    schema_handler.nest()
    schema_handler.data_bak2 = schema_handler.data
    schema_handler.write_json(out_json_pth_processed, pretty=True)

    assert schema_handler.data_bak1 == schema_handler.data_bak2

    lst = schema_handler.get_all_answer_types()

    return schema_handler



def start():
    schema_handler = get_schema_handler()
    for section_id in range(1, 9):
        schema_handler.set_section(section_id)
        formsets = schema_handler.get_formsets()

        print 'section_id: %s formsets: %s' % (section_id, len(formsets))

