import os
from glob import glob
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ihp.import2012.process import SubmissionParser

import override_5ga
import override_5gb

class Command(BaseCommand):
    #args = '<json file>'
    help = 'Import data from the questionnaires'

    def parse_file(self, f):
        try:
            parser = SubmissionParser.get_parser(f)
            submission = parser.process()
        except Exception, e:
            raise CommandError('[ERROR] Error processing file: %s (%s)' % (f, e))
    
    def handle(self, *args, **options):
        if len(args) == 1:
            self.parse_file(args[0])
        else:
            import_dir = os.path.join(settings.PROJECT_HOME, "dropbox") 
            if not os.path.exists(import_dir):
                raise CommandError("No drop folder found at %s" % import_dir)

            for f in glob("%s/*.xls" % import_dir):
                print 'Processing file: %s' % (f)
                self.parse_file(f)

        override_5ga.override_5Ga()
        override_5gb.override_5Gb()
