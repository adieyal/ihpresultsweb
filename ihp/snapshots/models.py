from django.db import models
from submissions.models import Agency, Country


# Create your models here.
class Case(models.Model):
    """
    Core model save calculation instances
    """
    name = models.CharField(max_length=150)

    calc_function = models.CharField(max_length=30)
    indicator = models.CharField(max_length=10, null=False)
    agency = models.ForeignKey(Agency, null=True)
    country = models.ForeignKey(Country, null=True)
    funcs = models.CharField(max_length=10, null=True)

    creation = models.DateTimeField('creation date', auto_now_add=True)

    def __unicode__(self):
        return self.name


class Version(models.Model):
    """
    Version model to save description for each run caserun set
    """
    description = models.CharField(max_length=250, null=True)
    creation = models.DateTimeField('creation date', auto_now_add=True)

    def __unicode__(self):
        return '%s-%s' % (self.pk, self.description)


class CaseRun(models.Model):
    """
    model holds each run(version) of saved case set
    with description field version number or note can be saved
    """

    case = models.ForeignKey(Case)
    version = models.ForeignKey(Version, null=True)

    base_val = models.CharField(max_length=150, null=True)
    base_year = models.CharField(max_length=150, null=True)
    cur_val = models.CharField(max_length=150, null=True)
    cur_year = models.CharField(max_length=150, null=True)

    def __unicode__(self):
        return '%s-%s' % (self.case, self.version)


class CaseRunManualData(models.Model):
    """
    model holds each run(version) of saved case set
    with description field version number or note can be saved
    """

    case = models.ForeignKey(Case)

    base_val = models.CharField(max_length=150, null=True)
    base_year = models.CharField(max_length=150, null=True)
    cur_val = models.CharField(max_length=150, null=True)
    cur_year = models.CharField(max_length=150, null=True)

    def __unicode__(self):
        return '%s' % self.case
