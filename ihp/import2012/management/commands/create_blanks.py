from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from submissions.models import *
import json

class Command(BaseCommand):
    args = '<json file>'
    help = 'Import data from the 2012 system'

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        questions = [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            "11", "12", "13", "14", "15", "16", "17", "18", "10old", "11old",
        ]
        for submission in Submission.objects.all():
            for question_number in questions:
                _, created = DPQuestion.objects.get_or_create(
                    submission=submission,
                    question_number=question_number
                )
                if created:
                    print "Created %s for %s in %s" % (question_number, submission.agency, submission.country)
                
