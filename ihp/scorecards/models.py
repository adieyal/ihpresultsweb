from django.db import models
import submissions.models as smodels
from submissions.models import Agency, GovQuestion
from submissions import target
from django.conf import settings

r0 = lambda x : round(float(x), 0)
r1 = lambda x : round(float(x), 1)
def foz(x):
    try:
        return float(x)
    except:
        return 0

def in_millions(x):
    return float(x) / 1000000

rating_icon = lambda icon : "%sicons/%s.svg" % (media_url, icon)
media_url = settings.MEDIA_URL

class GovScorecard(object):
    def __init__(self, country):
        self.country = country
        submission = self.submission = smodels.GovQuestion.objects.get(
            question_number=1, 
            submission__country=country
        ).submission
        self.gov_ltv = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).latest_value
        self.gov_lty = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).latest_year
        self.gov_blv = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).baseline_value
        self.gov_bly = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).baseline_year

        answers = {
            "yes" : "tick",
            True : "tick",
            "no" : "cross",
            False : "cross",
            "under_development" : "cross",
            "" : "line",
        }
        self.gov_rating = lambda qnum : rating_icon(answers[self.gov_ltv(qnum)])
        self.ratings = target.calc_country_ratings(country)
    
    def question(self, qnum):
        return smodels.GovQuestion.objects.get(question_number=qnum, submission=self.submission)

    def get_health_finance(self):
        external_baseline = r0(in_millions(foz(self.question("6").baseline_value)))
        external_latest = r0(in_millions(foz(self.question("6").latest_value)))
        domestic_baseline = r0(in_millions(foz(self.question("7").baseline_value))) - external_baseline
        domestic_latest = r0(in_millions(foz(self.question("7").latest_value))) - external_latest

        allocated_to_health = external_latest / r0(in_millions(foz(self.question("5").latest_value))) * 100
        increase = 15 - allocated_to_health

        return {
            "total": {
                "series":[
                    {
                        "name": self.question("6").baseline_year, 
                        "domestic": domestic_baseline,
                        "external": external_baseline
                    },
                    {
                        "name": 2010, 
                        "domestic": 0, 
                        "external": 0
                    },
                    {
                        "name": self.question("6").latest_year, 
                        "domestic": domestic_latest,
                        "external": external_latest
                    }
                ]
            },

            "budget": {
                "allocated": r1(allocated_to_health),
                "increase": r1(increase)
            },

            "pooled": self.question("17").latest_value
        }

    def get_systems(self):
        return {
            "management":{
                "header": "REFLECTS GOOD PRACTICE (OR REFORM IN PROGRESS)",
                "logo": rating_icon(self.ratings["5Ga"]["target"]),
                "description": "Homines plous oinvorsei virei atque mulieres sacra ne quisquam ecise velet, neve inter ibei virei plous duobus, mulieribus plous tribus arfuise velent, nisei de praitoris urbani senatuosque sententiad, utei suprad scriptum est."
            },

            "procurement": {
                "header": "REFLECTS GOOD PRACTICE (OR REFORM IN PROGRESS)",
                "logo": rating_icon(self.ratings["5Gb"]["target"]),
                "description": "Homines plous oinvorsei virei atque mulieres sacra ne quisquam ecise velet, neve inter ibei virei plous duobus, mulieribus plous tribus arfuise velent, nisei de praitoris urbani senatuosque sententiad, utei suprad scriptum est."
            },

            "technical": {
                "header": "DONOR CAPACITY DEVELOPMENT PROVIDED THROUGH COORDINATED PROGRAMMES",
                "logo": "icons/question.svg",
                "description": "Homines plous oinvorsei virei atque mulieres sacra ne quisquam ecise velet, neve inter ibei virei plous duobus, mulieribus plous tribus arfuise velent, nisei de praitoris urbani senatuosque sententiad, utei suprad scriptum est."
            }
        }
