import os, json, collections, copy

from datetime import datetime, date
from decimal import Decimal, InvalidOperation, DivisionByZero

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.html import mark_safe
from django.core.files.storage import FileSystemStorage

from jsonfield import JSONField

YEAR_CHOICES = tuple([(y, y) for y in range(2010, date.today().year + 2,)])

NOPLACES = Decimal(0)
THREEPLACES = Decimal(10) ** -3


# This needs to be changed to be dynamic.
SURVEY_SECTION_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8')
)


SURVEY_RESPONSE_CHOICES = (
    ('draft', 'Draft'),
    ('ready', 'Submitted'),
    ('reviewed', 'Reviewed'),
    ('verified', 'Verified'),
    ('jury', 'Jury'),
    ('completed', 'Completed')
)



class Survey(models.Model):
    """ This is the survey configuration.
    It's stored in the database as JSON.
    It can be built from JSON or CSV
    It can export as JSON or CSV
    Every change will update the timestamp and version.

    Changing the survey schema of a survey updates the survey version and hash.
    When a bound survey is generated using a previous response-set, the version and
    hash is checked to make sure the appropriate response-set is used for the
    appropriate survey.  If there is a difference between the two, questions that
    have been modified are reported to the user, asking for review.  Questions that
    are new are reported to the user, asking for responses.  Orphaned responses (those
        whos questions have been deleted/removed) are ignored.
    """

    title = models.CharField('title', max_length=100)
    description = models.TextField('description', null=True, blank=True)
    data = JSONField('data', load_kwargs={'object_pairs_hook': collections.OrderedDict}, editable=False)
    created_at = models.DateTimeField('created', null=True, blank=True, default=datetime.now)
    updated_at = models.DateTimeField('updated', null=True, blank=True)
    version = models.CharField('version', editable=False, max_length=100, null=True, blank=True)
    notifiers = models.ManyToManyField('SurveyNotifier', verbose_name='notifiers', blank=True, null=True)


    class Meta:
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'


    def __unicode__(self):
        return '%s' % self.title


    def save(self, *args, **kwargs):
        self.updated_at = datetime.today()
        if not self.id:
            self.created_at = datetime.today()

        return super(Survey, self).save(*args, **kwargs)



class SurveyNotifier(models.Model):
    """ This person is notified when a new survey response is submitted. """
    name = models.CharField("Name", max_length=499)
    email = models.EmailField("Email")

    def __unicode__(self):
        return "%s: %s" % (self.name, self.email)

    def save(self, *args, **kwargs):
        return super(SurveyNotification, self).save(*args, **kwargs)




class SurveyResponseManager(models.Manager):
    def get_queryset(self):
        return super(SurveyResponseManager, self).get_queryset().filter(deleted=False)

    def for_company(self):
        return self.filter(deleted=False).order_by('-year')

    def for_verifier(self, user):
        assigned = user.companies.all()
        queryset = self.filter(submitted=True, reviewed=True, verified=False, deleted=False, company__certification_level__in=['committed', 'certified'], company__in=assigned)
        return queryset.order_by('updated_at', 'company')

    def for_verifier_history(self, user):
        assigned = user.companies.all()
        queryset = self.filter(submitted=True, reviewed=True, verified=True, deleted=False, company__certification_level__in=['committed', 'certified'], company__in=assigned)
        return queryset.order_by('company', 'year')




class SurveyResponse(models.Model):
    objects = SurveyResponseManager()
    survey = models.ForeignKey('supasurvey.Survey', verbose_name='survey', related_name='submissions')
    year = models.IntegerField('year', choices=YEAR_CHOICES, null=True, blank=True)
    status = models.CharField('state', choices=SURVEY_RESPONSE_CHOICES, max_length=255, null=True, blank=True)

    completion = models.CharField('completion', max_length=255, null=True, blank=True)
    max_score = models.CharField('max score', max_length=255, null=True, blank=True)
    verified_score = models.CharField('verified score', max_length=255, null=True, blank=True)
    computed_score = models.CharField('computed score', max_length=255, null=True, blank=True)

    created_at = models.DateTimeField('created', null=True, blank=True, default=datetime.now)
    updated_at = models.DateTimeField('updated', null=True, blank=True)

    submitted = models.BooleanField('submitted', default=False)
    reviewed = models.BooleanField('reviewed', default=False)
    verified = models.BooleanField('verified', default=False)
    completed = models.BooleanField('completed', default=False)
    deleted = models.BooleanField('deleted', default=False)


    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'


    def __unicode__(self):
        return '%s' % self.company


    def set_verified():
        self.verified = True
        self.status = 'verified'
        self.save()


    def set_submitted():
        self.submitted = True
        self.status = 'ready'
        self.save()


    def get_all_sections(self):
        sections = []
        for section_id, section_key in SURVEY_SECTION_CHOICES:
            section = self.get_section_context(
                section_id = section_id,
                response_edit = False,
                verifier_edit = False,
                data = None,
                files = None
            )
            sections.append(section)

        return sections


    def get_storage(self):
        location = settings.REPORT_ROOT + '/%s/' % self.id
        base_url = settings.REPORT_URL + '%s/' % self.id

        return FileSystemStorage(location = location, base_url = base_url)


    @property
    def view(self, *args, **kwargs):
        pages = ['<a href="%s">(%s)</a>' % ((self.get_edit_url() + '?section=%s' % page), page) for page in range(1, 9)]

        return mark_safe(' '.join(pages))


    @property
    def can_view(self):
        return True


    @property
    def can_edit(self):
        if self.submitted:
            return False
        if self.deleted:
            return False
        return True


    @property
    def can_delete(self):
        if self.submitted:
            return False
        if self.deleted:
            return False
        return True


    @models.permalink
    def get_edit_url(self):
        return ('report-edit', None, {
            'id': self.id
        })


    @models.permalink
    def get_delete_url(self):
        return ('report-delete', None, {
            'id': self.id
        })


    @models.permalink
    def get_view_url(self):
        return ('report-view', None, {
            'id': self.id
        })


    def get_schema_handler(self):
        try:
            return self._schema_handler
        except AttributeError:
            from supasurvey.utils import get_schema_handler

            self._schema_handler = get_schema_handler(self)
            return self._schema_handler


    def get_completion_for_section(self, section_id):
        question_responses = self.question_responses.filter(survey_section=section_id)
        num = len(question_responses)

        try:
            total = sum([Decimal(question_response.fields_total) for question_response in question_responses])
            complete = sum([Decimal(question_response.fields_complete) for question_response in question_responses])
        except TypeError, e:
            total = Decimal(0)
            complete = Decimal(0)

        try:
            percentage = (Decimal(complete) / Decimal(total)) * 100
        except InvalidOperation, e:
            percentage = Decimal(0)
        except DivisionByZero, e:
            percentage = Decimal(0)

        return percentage


    def get_max_score_for_section(self, section_id):
        question_responses = self.question_responses.filter(survey_section=section_id)
        num = len(question_responses)

        try:
            total = sum([Decimal(question_response.max_score) for question_response in question_responses])
        except TypeError, e:
            total = Decimal(0)

        return total


    def get_verified_score_for_section(self, section_id):
        question_responses = self.question_responses.filter(survey_section=section_id)
        num = len(question_responses)

        try:
            total = sum([Decimal(question_response.verified_score) for question_response in question_responses])
        except TypeError, e:
            total = Decimal(0)

        return total


    def get_computed_score_for_section(self, section_id):
        question_responses = self.question_responses.filter(survey_section=section_id)
        num = len(question_responses)

        try:
            total = sum([Decimal(question_response.computed_score) for question_response in question_responses])
        except TypeError, e:
            total = Decimal(0)

        return total


    def get_completion(self):
        percentage = Decimal(0)
        total = Decimal(0)

        for section_id, section_key in SURVEY_SECTION_CHOICES:
            total += self.get_completion_for_section(section_id)

        percentage = (total / Decimal(len(SURVEY_SECTION_CHOICES)))

        return percentage.quantize(NOPLACES)


    def get_max_score(self):
        total = Decimal(0)

        for section_id, section_key in SURVEY_SECTION_CHOICES:
            total += self.get_max_score_for_section(section_id)

        return total.quantize(THREEPLACES)


    def get_verified_score(self):
        total = Decimal(0)

        for section_id, section_key in SURVEY_SECTION_CHOICES:
            total += self.get_verified_score_for_section(section_id)

        return total.quantize(THREEPLACES)


    def get_computed_score(self):
        total = Decimal(0)

        for section_id, section_key in SURVEY_SECTION_CHOICES:
            total += self.get_computed_score_for_section(section_id)

        return total.quantize(THREEPLACES)


    def get_formsets(self, **kwargs):
        section_id = kwargs.get('section_id')
        section_schema = kwargs.get('section_schema')
        response_edit = kwargs.get('response_edit', False)
        verifier_edit = kwargs.get('verifier_edit', False)
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)

        questionsets = self.get_schema_handler().get_questionsets(section_id)
        formsets = collections.OrderedDict()

        for questionset_id, questionset_schema in questionsets.items():
            prefix = 'fs_%s' % questionset_id

            question_response, created = QuestionResponse.objects.get_or_create(
                number = int(questionset_id),
                survey_response = self,
                survey_section = int(section_id)
            )

            formsets[questionset_id] = question_response.create_formset(
                questionset_schema = questionset_schema,
                response_edit = response_edit,
                verifier_edit = verifier_edit,
                prefix = prefix,
                data = data,
                files = files
            )

        return formsets


    def get_section_context(self, *args, **kwargs):
        section_id = kwargs.get('section_id')
        response_edit = kwargs.get('response_edit', False)
        verifier_edit = kwargs.get('verifier_edit', False)
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)

        section_schema = self.get_schema_handler().get_section_schema(section_id)

        section_formsets = self.get_formsets(
            section_id = section_id,
            section_schema = section_schema,
            response_edit = response_edit,
            verifier_edit = verifier_edit,
            data = data,
            files = files
        )


        section_files = []

        for question_id, formset in section_formsets.items():
            question_response = formset.meta.get('question_response')
            if question_response.uploaded_files.all():
                section_files.append(formset)

        ctx = {
            'display': section_schema.get('display'),
            'title': section_schema.get('title'),
            'completion': self.get_completion_for_section(section_id).quantize(NOPLACES),
            'formsets': section_formsets,
            'files': section_files
        }

        return ctx


    def create_questions(self):
        for section_id, section_key in SURVEY_SECTION_CHOICES:
            questionsets = self.get_schema_handler().get_questionsets(section_id)

            for questionset_id, questionset_schema in questionsets.items():
                QuestionResponse.objects.create(
                    number = int(questionset_id),
                    survey_response = self,
                    survey_section = int(section_id),
                    schema_data = questionset_schema
                )


    def calculate_scores(self):
        self.completion = self.get_completion()
        self.max_score = self.get_max_score()
        self.verified_score = self.get_verified_score()
        self.computed_score = self.get_computed_score()

        if Decimal(self.computed_score) > Decimal(self.max_score):
            self.computed_score = self.max_score


    def save(self, *args, **kwargs):
        self.updated_at = datetime.today()
        if not self.id:
            self.created_at = datetime.today()

        super(SurveyResponse, self).save(*args, **kwargs)


    def post_create(self):
        self.create_questions()
        self.calculate_scores()
        self.save()









class QuestionResponse(models.Model):
    number = models.IntegerField('question number', null=False, blank=False)
    survey_response = models.ForeignKey('supasurvey.SurveyResponse', verbose_name='Survey Response', related_name='question_responses')
    survey_section = models.IntegerField('section', choices=SURVEY_SECTION_CHOICES, max_length=255, null=True, blank=True)

    schema_data = JSONField('schema data', load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True, blank=True)
    response_data = JSONField('response data', load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True, blank=True)
    verifier_notes = JSONField('verifier notes', load_kwargs={'object_pairs_hook': collections.OrderedDict}, editable=False, null=True, blank=True)

    completion = models.CharField('completion', max_length=255, null=True, blank=True)
    fields_total = models.CharField('fields total', max_length=255, null=True, blank=True)
    fields_complete = models.CharField('fields complete', max_length=255, null=True, blank=True)
    completed = models.CharField('completed', max_length=255, null=True, blank=True)

    max_score = models.CharField('max score', max_length=255, null=True, blank=True)
    verified_score = models.CharField('verified score', max_length=255, null=True, blank=True)
    computed_score = models.CharField('computed score', max_length=255, null=True, blank=True)

    created_at = models.DateTimeField('created', null=True, blank=True, default=datetime.now)
    updated_at = models.DateTimeField('updated', null=True, blank=True)


    class Meta:
        verbose_name = 'Question Response'
        verbose_name_plural = 'Question Responses'
        ordering = ['survey_section', 'number']


    def __unicode__(self):
        return '%s-%s-%s' % (self.survey_response, self.survey_section, self.number)


    def post_create(self):
        if not self.schema_data:
            self.schema_data = {}
        if not self.response_data:
            self.response_data = []

        self.save()



    def save(self, *args, **kwargs):
        self.updated_at = datetime.today()
        if not self.id:
            self.created_at = datetime.today()
        else:
            self.calculate_scores()

        return super(QuestionResponse, self).save(*args, **kwargs)


    def calculate_scores(self):
        self.completion = self.calculate_completion()
        self.max_score = self.calculate_maxscore()
        self.fields_total = self.calculate_fields_total()
        self.fields_complete = self.calculate_fields_complete()
        self.computed_score = self.calculate_computed_score()

        if Decimal(self.computed_score) > Decimal(self.max_score):
            self.computed_score = self.max_score


    def calculate_fields_complete(self):
        total_fields = Decimal(0)
        response_data = self.response_data
        schema_data = self.schema_data

        # assert isinstance(schema_data, dict), '%s is not a dict' % schema_data
        # assert isinstance(response_data, list), '%s is not a list' % response_data

        if not isinstance(schema_data, dict):
            return Decimal(0)

        if not isinstance(response_data, list):
            return Decimal(0)

        answers = schema_data.get('answers', {})
        scored = [int(x.get('id')) for x in answers.values() if x.get('type') != 'file-multiple']

        try:
            completed = []
            for response in response_data:
                fields_completed = []

                for field_id, field_value in response.items():
                    answer_id = field_id.split('_')[-1]
                    if field_value and int(answer_id) in scored:
                        fields_completed.append(field_id)

                completed.append(len(fields_completed))

            return Decimal(max(completed))
        except ValueError, e:
            print 'calculate_fields_complete', e
            return Decimal(0)


    def calculate_fields_total(self):
        total_fields = Decimal(0)
        response_data = self.response_data
        schema_data = self.schema_data

        # assert isinstance(schema_data, dict), '%s is not a dict' % schema_data
        # assert isinstance(response_data, list), '%s is not a list' % response_data

        if not isinstance(schema_data, dict):
            return Decimal(0)

        if not isinstance(response_data, list):
            return Decimal(0)

        answers = schema_data.get('answers', {})
        scored = [int(x.get('id')) for x in answers.values() if x.get('type') != 'file-multiple']

        return Decimal(len(scored))


    def is_scoring(self):
        if self.max_score:
            return Decimal(self.max_score) > Decimal(0)
        return False


    def get_max_score(self):
        if self.max_score:
            return Decimal(self.max_score)
        return Decimal(0)


    def calculate_completion(self):
        percentage = Decimal(0)

        fields_complete = self.calculate_fields_complete()
        fields_total = self.calculate_fields_total()

        try:
            percentage = (fields_complete / fields_total) * 100
        except InvalidOperation, e:
            percentage = Decimal(0)
        except DivisionByZero, e:
            percentage = Decimal(0)

        if int(fields_total) == 0:
            return 'N/A'
        return '%s' % percentage.quantize(THREEPLACES)


    def get_correct_score(self, correct, field_type, field_value, min_score, max_score):
        if isinstance(field_value, list):
            v = field_value[0]
        elif isinstance(field_value, tuple):
            v = field_value[0]
        else:
            v = field_value

        if v.lower() == correct.lower():
            return max_score
        return min_score


    def get_choice_score(self, scoring, field_type, field_options, field_value, min_score, max_score):
        scores = scoring.split('|')
        options = field_options.split('|')
        _score = Decimal(0)

        if field_type == 'radio':
            if isinstance(field_value, tuple) and (len(field_value) == 2):
                value = field_value[0]
            elif isinstance(field_value, list) and (len(field_value) == 2):
                value = field_value[0]
            else:
                value = field_value

            if isinstance(value, str):
                value = unicode(value)

            if value in options:
                index = options.index(value)
                _score = Decimal(scores[index])

        elif field_type == 'radio-open':
            if isinstance(field_value, tuple) and (len(field_value) == 2):
                value = field_value[0]
            elif isinstance(field_value, list) and (len(field_value) == 2):
                value = field_value[0]
            else:
                value = field_value

            if value in options:
                index = options.index(value)
                _score = Decimal(scores[index])

        elif field_type == 'radio-yes-no':
            if isinstance(field_value, tuple) and (len(field_value) == 2):
                value = field_value[0]
            elif isinstance(field_value, list) and (len(field_value) == 2):
                value = field_value[0]
            else:
                value = field_value

            if value in options:
                index = options.index(value)
                _score = Decimal(scores[index])

        elif field_type == 'checkbox':
            assert isinstance(field_value, list), '%s is not list' % type(field_value)
            for value in field_value:
                if value in options:
                    index = options.index(value)
                    _score += Decimal(scores[index])

        return _score


    def get_score(self, field_id, field_value):
        schema_data = self.schema_data
        answer_id = field_id.split('_')[-1]
        answers = schema_data.get('answers')
        answer_dct = answers.get(answer_id)

        field_options = answer_dct.get('options', False)
        field_type = answer_dct.get('type')
        field_correct = answer_dct.get('correct', False)
        field_scoring = answer_dct.get('scoring', False)
        min_score = Decimal(answer_dct.get('minscore', '0'))
        max_score = Decimal(answer_dct.get('maxscore', '0'))

        _score = min_score

        if field_scoring and field_options:
            _score = self.get_choice_score(field_scoring, field_type, field_options, field_value, min_score, max_score)
        elif field_correct:
            _score = self.get_correct_score(field_correct, field_type, field_value, min_score, max_score)

        return _score


    def calculate_computed_score(self):
        total_score = Decimal(0)

        response_data = self.response_data

        for response in response_data:
            for field_id, field_value in response.items():
                if field_value:
                    score = self.get_score(field_id, field_value)
                    total_score += Decimal(score)

        return total_score.quantize(THREEPLACES)


    def calculate_maxscore(self):
        total_maxscore = Decimal(0)

        answers = self.schema_data.get('answers')
        for answer_id, answer_dct in answers.items():
            maxscore = answer_dct.get('maxscore', None)
            if maxscore:
                total_maxscore += Decimal(maxscore)

        return total_maxscore.quantize(THREEPLACES)


    def get_storage(self):
        return self.survey_response.get_storage()


    def delete_file(self, filename):
        storage = self.get_storage()

        try:
            uploaded_file = self.uploaded_files.get(id = filename)
            storage.delete(uploaded_file.basename)
            uploaded_file.delete()
        except ValueError, e:
            pass

        return filename


    def upload_file(self, file_obj):
        storage = self.get_storage()

        relpath = os.path.normpath(storage.get_valid_name(os.path.basename(file_obj.name)))
        filename = storage.save(relpath, file_obj)
        uploaded_file = self.uploaded_files.create(upload = filename)

        return uploaded_file.id


    def delete_files(self, filenames):
        return [self.delete_file(file_id) for file_id in filenames]


    def upload_files(self, files):
        filenames = [self.upload_file(file_obj) for file_obj in files]
        return filenames


    def process_files_for_field(self, data, fieldname):
        """ cleaned_clearableupload is tuple(original_list, to_add, to_remove) """
        cleaned_clearableupload = data.pop(fieldname, None)
        original_set = []

        if cleaned_clearableupload:
            original = cleaned_clearableupload[0]
            added = cleaned_clearableupload[1]
            removed = cleaned_clearableupload[2]

            original_set = set(original)

            if removed:
                removed_set = set(self.delete_files(removed))
                original_set.difference_update(removed_set)

            if added:
                added_set = set(self.upload_files(added))
                original_set.update(added_set)

        return list(original_set)


    def get_verifier_initial(self):
        dct = {}

        verifier_notes = self.verifier_notes or None
        verifier_score = self.verified_score or None

        if verifier_notes:
            dct['notes'] = verifier_notes

        if verifier_score:
            dct['score'] = verifier_score

        return dct


    def create_formset(self, **kwargs):
        from supasurvey.forms import SupaSurveyForm, SupaSurveyFormSet, VerifierForm
        from django.forms.formsets import formset_factory

        questionset_schema = kwargs.get('questionset_schema')
        prefix = kwargs.get('prefix')
        response_edit = kwargs.get('response_edit', False)
        verifier_edit = kwargs.get('verifier_edit', False)
        data = kwargs.get('data', None)
        files = kwargs.get('files', None)

        response_initial = self.response_data or None
        verifier_initial = self.get_verifier_initial()

        qss = questionset_schema
        is_repeater = qss.get('repeater', False)
        repeater_label = qss.get('repeater_label', None)
        extra = 0 if response_initial else 1

        FormSet = formset_factory(SupaSurveyForm,
                extra=extra,
                formset=SupaSurveyFormSet)


        formset = FormSet(data, files,
                initial = response_initial,
                prefix = prefix,
                edit = response_edit,
                schema = qss)

        question_id = qss.get('id')
        question_title = qss.get('title', None)
        question_description = qss.get('description', None)
        question_dependencies = qss.get('dependencies', None)
        verifier_prefix = 'q-%s_verifier' % question_id
        max_score = self.get_max_score()

        verifier_form = VerifierForm(
                edit = verifier_edit,
                max_score = max_score,
                data = data,
                initial = verifier_initial,
                prefix = verifier_prefix)


        formset.meta = {
            'verifier_form': verifier_form,
            'id': question_id,
            'title': question_title,
            'description': question_description,
            'dependencies': question_dependencies,
            'repeater': is_repeater,
            'repeater_label': repeater_label,
            'prefix': prefix,
            'question_response': self
        }

        return formset


    def process_response_data(self, data):
        if data:
            self.response_data = data


    def process_verifier_data(self, data):
        if data:
            verifier_notes = data.get('notes', None)
            verifier_score = data.get('score', None)
            if verifier_notes:
                self.verifier_notes = verifier_notes
            if verifier_score:
                self.verified_score = verifier_score



class UploadedFile(models.Model):
    def upload_to(instance, name):
        report_id = instance.question_response.survey_response.id
        return settings.REPORT_ROOT + '/%s/%s' % (report_id, name)


    upload = models.FileField(upload_to=upload_to, max_length=400)
    question_response = models.ForeignKey('QuestionResponse', verbose_name='question_responses', related_name='uploaded_files')
    created_at = models.DateTimeField('created', null=True, blank=True, default=datetime.now)
    updated_at = models.DateTimeField('updated', null=True, blank=True)


    class Meta:
        verbose_name = 'Uploaded File'
        verbose_name_plural = 'Uploaded Files'


    def __unicode__(self):
        return '%s (%s)' % (self.question_response, self.basename)

    @property
    def basename(self):
        return self.upload.url.split('/')[-1]

    def save(self, *args, **kwargs):
        self.updated_at = datetime.today()
        if not self.id:
            self.created_at = datetime.today()

        return super(UploadedFile, self).save(*args, **kwargs)


    def get_absolute_url(self):
        report_id = self.question_response.survey_response.id
        return settings.REPORT_URL + '%s/%s' % (report_id, self.basename)


def post_survey_create(sender, instance, created, *args, **kwargs):
    if created:
        instance.post_create()


def post_question_create(sender, instance, created, *args, **kwargs):
    if created:
        instance.post_create()


post_save.connect(post_survey_create, sender=SurveyResponse)
post_save.connect(post_question_create, sender=QuestionResponse)
