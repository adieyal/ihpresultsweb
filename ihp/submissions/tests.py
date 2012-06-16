from django.test import TestCase
from submissions.models import GovQuestion, CurrencyConversion

class GovQuestionTest(TestCase):
    def test_convert_dollars(self):
        """
        Tests that 1 + 1 always equals 2.
        """

        q = GovQuestion()
        q.baseline_value = 100
        q.baseline_year = 2010
        q.latest_value = 200
        q.latest_year = 2010
        
        self.failUnlessEqual(q.base_val_as_dollars, 100)
        self.failUnlessEqual(q.cur_val_as_dollars, 200)

        q.baseline_value = "USD100"
        self.failUnlessEqual(q.base_val_as_dollars, 100)

    def test_convert_invalid_string(self):
        """
        Tests that 1 + 1 always equals 2.
        """

        q = GovQuestion()
        q.baseline_value = ""
        
        self.assertRaises(Exception, q._as_dollars, (q.baseline_value, 2010))

        q.baseline_value = None
        self.assertRaises(Exception, q._as_dollars, (q.baseline_value, 2010))

        q.baseline_value = "XXXXXX"
        self.assertRaises(Exception, q._as_dollars, (q.baseline_value, 2010))

    def test_other_currency(self):
        CurrencyConversion.objects.create(
            year=2010,
            currency="tst",
            rate=2
        )

        q = GovQuestion()
        q.baseline_value = "tst100"
        q.baseline_year = 2010
        q.latest_value = "tst200"
        q.latest_year = 2010

        self.failUnlessEqual(q.base_val_as_dollars, 200)
        self.failUnlessEqual(q.cur_val_as_dollars, 400)
