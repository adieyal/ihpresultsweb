import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core import management
from submissions.models import *
from submissions.indicators import *
from ihp.snapshots.models import Version,Case,CaseRun


class Command(BaseCommand):
    args = "Optional description for version"
    help = "Take snaphot of function results for current state of submissions"

    def calc_agency_country_indicator_dp(self, version):
        print "processing %s " % "calc_agency_country_indicator_dp"
        agency_countries = AgencyCountries.objects.all()
        funcs = None

        for i in agency_countries:
            agency = i.agency
            country = i.country

            calc_function = 'calc_agency_country_indicator'

            qs = DPQuestion.objects.filter(submission__agency=agency,
                            submission__country=country).select_related()

            for j in dp_indicators:
                a, b = calc_agency_country_indicator(qs, agency, country, j,
                                                     funcs)
                name = '%s_%s_%s_%s_%s' % (calc_function, agency, country, j,
                                        funcs)
                print "saving %s" % name
                c, created = Case.objects.get_or_create(name=name,
                                               calc_function=calc_function,
                                               indicator=j, agency=agency,
                                               country=country, funcs=funcs)

                CaseRun(version=version, case=c,
                            base_val=a[0],
                            base_year=a[1],
                            cur_val=a[2],
                            cur_year=a[3]).save()

    def snapshot(self, desc=None):
        v = Version(description=desc)
        v.save()
        print "started to snapshot %s" % v
        self.calc_agency_country_indicator_dp(v)
        print "end snapshot"

    def handle(self, *args, **options):
        if len(args) == 0:
            self.snapshot()
        else:
            self.snapshot(desc=args[0])
