"""
Tests for the public IHP website Django parts.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from submissions.models import Agency, Country, AgencyCountries
import submissions.target
import submissions.consts

from ihp.publicweb.views import agency_scorecard_page

class PublicWebsiteTest(TestCase):
    fixtures = ['indicator_tests']
    unicef = Agency.objects.get(agency="UNICEF")
    
    def test_getting_agency_countries(self):
        self.assertNotEqual(self.unicef, None)
        self.assertEqual(self.unicef.id, 27)
        
        mozambique = Country.objects.get(country="Mozambique")
        self.assertNotEqual(mozambique, None)
        self.assertEqual(mozambique.id, 9)
        
        agency_countries = AgencyCountries.objects.get_agency_countries(self.unicef)
        self.assertTrue(mozambique in agency_countries)
        
        self.assertTrue(submissions.target.country_agency_progress(mozambique, self.unicef))
        
        ratings = submissions.target.calc_agency_ratings(self.unicef)
        
        rating_1 = ratings['1DP']
        self.assertEqual(rating_1['base_val'], submissions.consts.NA_STR)
        self.assertEqual(rating_1['cur_val'], 100.0)
        self.assertEqual(rating_1['comments'], [(u'1', mozambique, u'')])
        # self.assertEqual(rating_1['comments'][0][0], '1')
        # self.assertEqual(rating_1['comments'][0][1], mozambique)
        # self.assertEqual(rating_1['comments'][0][2], '')
        # submissions.target.commentary_map['1DP'])
        self.assertEqual(rating_1['target'], submissions.target.Rating.TICK)
        self.assertEqual(rating_1['target_val'], 100.0)
        
    def test_country_scorecard_view(self):
        response = self.client.get(reverse(agency_scorecard_page,
            kwargs={'agency_name': self.unicef.agency}))
        self.assertEqual(response.context['agency'], self.unicef)
        