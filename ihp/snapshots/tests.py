"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from submissions.models import *
from submissions.indicators import *
from ihp.snapshots.models import Version, Case, CaseRun, CaseRunManualData


# python manage.py test submissions -v 2
class Test_calc_agency_country_indicator_dp(TestCase):
    fixtures = ['test_data1.json', 'all']

    def test_calc_agency_country_indicator_dp(self):
        v = Version.objects.latest('id')
        caseruns = [c.case.name for c in CaseRun.objects.filter(version=v)]
        calc_function = 'calc_agency_country_indicator'

        agency_countries = AgencyCountries.objects.filter(
                            agency__in=Agency.objects.all(),
                            country__in=Country.objects.all())
        funcs = None

        for i in agency_countries:
            agency = i.agency
            country = i.country
            for j in dp_indicators:
                name = '%s_%s_%s_%s_%s' % (calc_function, agency, country,
                                        j, funcs)
                print name
                if name in caseruns:
                    qs = DPQuestion.objects.filter(submission__agency=agency,
                                submission__country=country).select_related()
                    a, b = calc_agency_country_indicator(qs, agency, country,
                                                    j, funcs)
                    cr = CaseRun.objects.get(case__name=name, version=v)
                    cr_values = map(lambda x:str(x), [cr.base_val,cr.base_year,
                                            cr.cur_val,cr.cur_year])
                    a_values = map(lambda x:str(x), [a[0],a[1],a[2],a[3]])
                    
                    print "%s = %s :%s" % (cr_values,a_values,name)
                    self.assertEqual(cr_values, a_values)
                    
