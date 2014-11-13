import floppyforms as forms

from .fields import ChooseYesNoField, ChooseOneField, ChooseOneOpenField, ChooseMultipleField
from .fields import ChooseOneForEachField, OpenField, EmailField


REQUIRED = True



class SupaSurveyForm(forms.Form):
    pass


class SurveyFormSimple(SupaSurveyForm):
    """ This is an example of a static form with no scoring """
    name = TextField(label="What is your name?")
    
    email = EmailField(
        label="What is your email address?",
        required=REQUIRED)

    yes_no = ChooseYesNoField(
        label="Are you a good dog?", 
        required=REQUIRED)

    choose_one = ChooseOneField(
        label="If yes, how long have you been a good dog?", 
        choices = [
            "1-2 years",
            "3-5 years",
            "5-10 years"],
        stacked=True, 
        dependency="good_dog==YES",
        required=REQUIRED)


    choose_one_open = ChooseOneOpenField(
        label="How did you first hear about being a good dog?", 
        choices=[
            "A friend/family member told me about it",
            "I heard about it online",
            "I saw it at a bookstore",
            "I found it at a library",
            "I received an offer in the mail",
            "I have a copy in my office"],
        required=REQUIRED)


    write_anything = OpenField(
        label="How would you describe being a good dog to a friend?", 
        required=REQUIRED
        max_words=None,
        min_words=None)


    choose_multiple = ChooseMultipleField(
        label="What are you favorite parts of being a good dog??", 
        choices = [
            "Treats",
            "Pats on the head",
            "Belly rubs",
            "Toys",
            "Going to the beach",
            "Playing catch"
        ])


    choose_one_for_each = ChooseOneForEachField(
        label="For each activity, should there be more or less?",
        choices=[
            "More", 
            "Same", 
            "Less"],
        subjects=[
            "Treats", 
            "Pats on the head",
            "Belly rubs",
            "Toys",
            "Going to the beach",
            "Playing catch"],
        required=REQUIRED)


class SurveyFormScoring(SupaSurveyForm):
    """ This is an example of a form with Scoring """
    pass


class SurveyFormRepeater(SupaSurveyForm):
    """ This is an example of a form with a repeater question """
    pass