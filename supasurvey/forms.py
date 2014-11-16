import floppyforms as forms
from decimal import *

from .fields import ChooseYesNoField, ChooseOneField, ChooseOneOpenField, ChooseMultipleField
from .fields import CharField, EmailField, TextField, ChooseOneForEachField


REQUIRED = True



class SupaSurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SupaSurveyForm, self).__init__(*args, **kwargs)
        self._max_score = Decimal(0);
        self._score = Decimal(0);


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


# class SurveyFormSimple(SupaSurveyForm):
#     """ This is an example of a static form with no scoring """
#     name = CharField(label="What is your name?")
    
#     email = EmailField(
#         label="What is your email address?",
#         required=REQUIRED)

#     yes_no = ChooseYesNoField(
#         label="Are you a good dog?", 
#         required=REQUIRED)

#     choose_one = ChooseOneField(
#         label="If yes, how long have you been a good dog?", 
#         choices = [
#             "1-2 years",
#             "3-5 years",
#             "5-10 years"],
#         dependency="good_dog==YES",
#         required=REQUIRED)


#     choose_one_open = ChooseOneOpenField(
#         label="How did you first hear about being a good dog?", 
#         choices=[
#             "A friend/family member told me about it",
#             "I heard about it online",
#             "I saw it at a bookstore",
#             "I found it at a library",
#             "I received an offer in the mail",
#             "I have a copy in my office"],
#         required=REQUIRED)


#     write_anything = TextField(
#         label="How would you describe being a good dog to a friend?", 
#         required=REQUIRED)


#     choose_multiple = ChooseMultipleField(
#         label="What are you favorite parts of being a good dog??", 
#         choices = [
#             "Treats",
#             "Pats on the head",
#             "Belly rubs",
#             "Toys",
#             "Going to the beach",
#             "Playing catch"
#         ])


#     choose_one_for_each = ChooseOneForEachField(
#         label="For each activity, should there be more or less?",
#         choices=[
#             "More", 
#             "Same", 
#             "Less"],
#         subjects=[
#             "Treats", 
#             "Pats on the head",
#             "Belly rubs",
#             "Toys",
#             "Going to the beach",
#             "Playing catch"],
#         required=REQUIRED)


# class SurveyFormScoring(SupaSurveyForm):
#     """ This is an example of a form with Scoring """
#     pass


# class SurveyFormRepeater(SupaSurveyForm):
#     """ This is an example of a form with a repeater question """
#     pass