from datetime import datetime, timedelta

from django.db import models
from django.conf import settings

from jsonfield import JSONField


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

    title = models.CharField("Title", max_length=100)
    data = JSONField("Data")
    created = models.DateField("Created")
    updated = models.DateField("Updated")
    #start = models.DateField("Start")
    #end = models.DateField("End")
    #version = models.IntegerField("Version")
    #survey_hash = models.CharField("Survey Hash")
    notifiers = models.ForeignKey("SurveyNotifier", blank=True, null=True)
    # introduction = models.TextField("Introduction", blank=True, null=True)
    # completion = models.TextField("Completion", blank=True, null=True)

    def __unicode__(self):
        return "%s: %s" % (self.email, self.timestamp)

    def save(self, *args, **kwargs):
        if not self.id:
            self.updated = datetime.today()
        return super(Survey, self).save(*args, **kwargs)

    def export_as_JSON(self):
        pass

    def export_as_CSV(self):
        pass

    def import_as_JSON(self):
        pass

    def import_as_CSV(self):
        pass

    def notify_notifiers(self):
        pass

    def update_version(self):
        pass

    def update_hash(self):
        pass



class SurveyNotifier(models.Model):
    """ This person is notified when a new survey response is submitted. """
    name = models.CharField("Name", max_length=499)
    email = models.EmailField("Email")

    def __unicode__(self):
        return "%s: %s" % (self.name, self.email)

    def save(self, *args, **kwargs):
        return super(SurveyNotification, self).save(*args, **kwargs)



class SurveyResponse(models.Model):
    """ This is a survey response. I don't think it should contain any 
    user information, as that belongs in the user profile.  But it should
    be able to be linked to a user profile."""
    survey = models.ForeignKey("Survey")
    created = models.DateField("Created")
    updated = models.DateField("Updated")
    data = JSONField()

    def __unicode__(self):
        return "%s-%s, %s" % (self.survey.title, self.id, self.updated)

    def save(self, *args, **kwargs):
        self.updated = datetime.today()
        if not self.id:
            self.created = datetime.today()
        return super(SurveyResponse, self).save(*args, **kwargs)



