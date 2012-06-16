# -*- coding: utf-8 -*-
from django.db import models
import submissions.models as smodels
from submissions.models import Agency, GovQuestion, MDGData
from submissions import target
from django.conf import settings

def foz(x):
    try:
        return float(x)
    except:
        return 0
def myround(x, places=0):
    return round(foz(x), places)
r0 = lambda x : myround(x, 0)
r1 = lambda x : myround(x, 1)

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
        self.mdgs = MDGData.objects.filter(country=country)

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

    def get_health_systems(self):
        def latest_div_baseline(qnum):
            q = self.question(qnum)
            latest = foz(q.latest_value)
            baseline = foz(q.baseline_value)
            if baseline == 0:
                return 0
            return r1((latest / baseline) * 100)

        return {
            "phcclinincs": {
                "value": round(foz(self.question("20").latest_value) / 10000.0),
                "percent": latest_div_baseline("20")
            },
            "healthworkers": {
                "value": round(foz(self.question("18").latest_value) / 10000.0, 1),
                "percent": latest_div_baseline("18")
            },
            "healthsystems": {
                "value": self.question("21").cur_val_as_dollars,
                "percent": latest_div_baseline("21")
            }
        }

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

    def get_mdg_progress(self):
        poverty_mdg = self.mdgs.get(mdg_target="MDG1")
        education_mdg = self.mdgs.get(mdg_target="MDG2")
        gender_mdg = self.mdgs.get(mdg_target="MDG3")
        childmortality_mdg = self.mdgs.get(mdg_target="MDG4")
        maternalmortality_mdg = self.mdgs.get(mdg_target="MDG5a")
        familyplanning_mdg = self.mdgs.get(mdg_target="MDG5b")
        hiv_mdg = self.mdgs.get(mdg_target="MDG6a")
        under5_mdg = self.mdgs.get(mdg_target="MDG6b")
        tb_mdg = self.mdgs.get(mdg_target="MDG6c")
        water_mdg = self.mdgs.get(mdg_target="MDG7a")
        sanitation_mdg = self.mdgs.get(mdg_target="MDG7b")

        def gen_dict(mdg, is_percentage=True):
            color = "good" if mdg.arrow and "green" in mdg.arrow else "bad"
             
            d = {
                "color": color,

                "value": mdg.latest_value,
                "year": mdg.latest_year,


                "change_value": r1(mdg.change),
                "change_year": mdg.baseline_year,
                "arrow": "up" if mdg.is_increase else "down"
            }

            if is_percentage:
                d["change_type"] = "percent" 
                d["type"] = "percent"
            return d

        return {
            "poverty": gen_dict(poverty_mdg),
            "edictation": gen_dict(education_mdg),
            "gender": gen_dict(gender_mdg),
            "mortality": gen_dict(childmortality_mdg, False),
            "maternal_mortality": gen_dict(maternalmortality_mdg, False),
            "family_planning": gen_dict(familyplanning_mdg),
            "hiv": gen_dict(hiv_mdg),
            "children_u5": gen_dict(under5_mdg),
            "tb": gen_dict(tb_mdg, False),
            "water": gen_dict(water_mdg),
            "sanitation": gen_dict(sanitation_mdg) 
        }

    def get_ratings(self):
        r1G = self.ratings["1G"]
        r2Ga = self.ratings["2Ga"]
        r2Gb = self.ratings["2Gb"]
        r3G = self.ratings["3G"]
        r4G = self.ratings["4G"]
        r5Ga = self.ratings["5Ga"]
        r5Gb = self.ratings["5Gb"]
        r6G = self.ratings["6G"]
        r7G = self.ratings["7G"]
        r8G = self.ratings["8G"]

        def progress_to_int(val):
            return {
                "y" : 2, "yy" : 2, 100 : 2,
                0 : 0, "n" : 0, None : 0
            }[val]

        return {
            "mutual_agreement":{
                "description": "An IHP+ Compact or equivalent mutual agreement is in place.",
                "rating": rating_icon(r1G["target"]),
                "max": 2,
                "progress": [
                    {"year": r1G["base_year"], "value":progress_to_int(r1G["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r1G["cur_year"], "value":progress_to_int(r1G["cur_val"])},
                ]
            },
            "health_plan":{
                "description": "A NationalHealth Sector Plan/ Strategy is in place with current targets & budgets that have been jointly assessed.",
                "rating": rating_icon(r2Ga["target"]),
                "max": 2,
                "progress": [
                    {"year": r2Ga["base_year"], "value":progress_to_int(r2Ga["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r2Ga["cur_year"], "value":progress_to_int(r2Ga["cur_val"])},
                ]
            },
            "hrh_plan":{
                "description": "A costed, comprehensive national HRH plan (integrated with the health plan) is being implemented or developed.",
                "rating": rating_icon(r2Gb["target"]),
                "max": 2,
                "progress": [
                    {"year": r2Gb["base_year"], "value":progress_to_int(r2Gb["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r2Gb["cur_year"], "value":progress_to_int(r2Gb["cur_val"])},
                ]
            },
            "fundingcommitments":{
                "description": "15% (or an equivalent published target) of the national budget is allocated to health.",
                "rating": "icons/arrow.svg",
                "rating": rating_icon(r3G["target"]),
                "progress": [
                    {"year": r3G["base_year"], "value":foz(r3G["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r3G["cur_year"], "value":foz(r3G["cur_val"])},
                ],
                "line": { "constant": 15},
                "max": 20
            },
            "health_funding":{
                "description": "Halve the proportion of health sector funding not disbursed against the approved annual budget.",
                "rating": rating_icon(r4G["target"]),
                "progress": [
                    {"year": r4G["base_year"], "value":foz(r4G["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r4G["cur_year"], "value":foz(r4G["cur_val"])},
                ],
                "line": {"constant": 71},
                "max": 100
            },
            "cipa_scale":{
                "description": "Improvement of at least one measure (ie 0.5 points) on the PFM/CPIA scale of performance.",
                "rating": rating_icon(r5Ga["target"]),
                "progress": [
                    {"year": r5Ga["base_year"], "value":foz(r5Ga["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r5Ga["cur_year"], "value":foz(r5Ga["cur_val"])},
                ],
                "max": 5
            },
            "performance_scale":{
                "description": "Improvement of at least one measure on the four-point scale used to assess performance for this sector.",
                "rating": rating_icon(r5Gb["target"]),
                "type":"dot",
                "progress": [
                    {"year": r5Gb["base_year"], "value":foz(r5Gb["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r5Gb["cur_year"], "value":foz(r5Gb["cur_val"])},
                ]
            },

            "resources":{
                "description": "A transparent and monitorable performance assessment framework is in place to assess progress in the health sector.",
                "rating": rating_icon(r6G["target"]),
                "max": 2,
                "progress": [
                    {"year": r6G["base_year"], "value":progress_to_int(r6G["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r6G["cur_year"], "value":progress_to_int(r6G["cur_val"])},
                ]
            },
            "accountability":{
                "description": "Mutual assesments (such as joint Annual Health Sector Review) are being made of progress implementing commitments in the health sector, including on aid effectiveness.",
                "rating": rating_icon(r7G["target"]),
                "max": 2,
                "progress": [
                    {"year": r7G["base_year"], "value":progress_to_int(r7G["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r7G["cur_year"], "value":progress_to_int(r7G["cur_val"])},
                ]
            },
            "civilsociety":{
                "description": "At least 10% of seats in the country’s Health Sector Coordination mechanisms are allocated to Civil Society",
                "rating": rating_icon(r8G["target"]),
                "max": 2,
                "progress": [
                    {"year": r8G["base_year"], "value":progress_to_int(r8G["base_val"])},
                    {"year":"0", "value":0},
                    {"year": r8G["cur_year"], "value":progress_to_int(r8G["cur_val"])},
                ]
            }
        }
