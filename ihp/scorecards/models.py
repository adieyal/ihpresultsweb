# -*- coding: utf-8 -*-
from django.db import models
import submissions.models as smodels
from submissions.models import Agency, GovQuestion, MDGData, DPQuestion, AgencyTargets, CountryTargets
from submissions import indicators
from submissions import target
from django.conf import settings
from django.utils.translation import ugettext as _

#Nasty, I know.
from previous_data import get2010value, add_previous_value

def foz(x):
    try:
        return float(x)
    except:
        return 0

def safe_div(x, y):
    try:
        return float(x) / float(y)
    except:
        return None

def safe_mul(x, y):
    try:
        return float(x) * float(y)
    except:
        return None
    
def safe_diff(x, y):
    try:
        return x - y
    except:
        return None

def myround(x, places=0):
    return round(foz(x), places)
r0 = lambda x : myround(x, 0)
r1 = lambda x : myround(x, 1)
r2 = lambda x : myround(x, 2)

def in_millions(x):
    return float(x) / 1000000

rating_icon = lambda icon : "%sicons/%s.svg" % (media_url, icon)
media_url = settings.MEDIA_URL

class GovScorecard(object):
    def __init__(self, country, language):
        self.country = country
        self.language = language
        submission = self.submission = smodels.GovQuestion.objects.get(
            question_number=1, 
            submission__country=country
        ).submission
        self.gov_ltv = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).latest_value
        self.gov_lty = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).latest_year
        self.gov_blv = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).baseline_value
        self.gov_bly = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).baseline_year
        self.gov_comment = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).comments
        self.mdgs = MDGData.objects.filter(country=country)

        answers = {
            "yes" : "tick",
            True : "tick",
            "no" : "cross",
            False : "cross",
            "under_development" : "cross",
            "" : "line",
        }

        def get_rating(val):
            if val == None:
                return "question"
            return answers.get(val.lower(), "question")
        self.gov_rating = lambda qnum : rating_icon(get_rating(self.gov_ltv(qnum)))
        self.tick_if_true = lambda val : rating_icon("tick") if val else rating_icon("cross")
        self.ratings = target.calc_country_ratings(country)
    
    def question(self, qnum):
        return smodels.GovQuestion.objects.get(question_number=qnum, submission=self.submission)

    def get_managing_for_results(self):
        return {
            "national_results": self.gov_rating("11"),
            "functional_health": self.gov_rating("22"),
            "decisons_results": self.gov_rating("11"),
            "joint_health": self.gov_rating("12"),
        }

    def get_health_systems(self):
        def latest_div_baseline(qnum):
            q = self.question(qnum)
            latest = q.cur_val_as_dollars
            baseline = q.base_val_as_dollars
            try:
                if baseline == 0:
                    return None
                return (latest / baseline) * 100
            except:
                return None

        def proportions(cur, base):
            v = safe_div(cur, base)
            if v == None: return None

            return (v - 1) * 100

        def for_10000_population(val, baseline=False):
            population_cur = self.question("19").cur_val
            population_base = self.question("19").base_val
            if baseline:
                return safe_mul(safe_div(val, population_base), 10000)
            else:
                return safe_mul(safe_div(val, population_cur), 10000)

        try:
            healthsystems = self.question("21").cur_val_as_dollars
        except Exception:
            healthsystems = None


        phcclinics_cur = for_10000_population(self.question("20").cur_val)
        phcclinics_base = for_10000_population(self.question("20").base_val, True)
        healthworkers_cur = for_10000_population(self.question("18").cur_val)
        healthworkers_base = for_10000_population(self.question("18").base_val, True)
        
        no_data_available = _("No data available")
        return {
            "phcclinincs": {
                "value": phcclinics_cur,
                "percent": proportions(phcclinics_cur, phcclinics_base),
                "missing_data_text" : no_data_available
            },
            "healthworkers": {
                "value": healthworkers_cur,
                "percent": proportions(healthworkers_cur, healthworkers_base),
                "missing_data_text" : no_data_available
            },
            "healthsystems": {
                "value": healthsystems,
                "percent": safe_diff(latest_div_baseline("21"), 100),
                "missing_data_text" : no_data_available
            }
        }

    def get_country_ownership(self):
        if self.gov_ltv("13") == None:
            cs_logo = rating_icon("question")
        else:
            cs_logo = self.tick_if_true(foz(self.gov_ltv("13")) >= 10)

        # % of seats to CS calculation.
        if foz(self.question("5").latest_value) > 0:
            seats = foz(self.question("6").latest_value)/foz(self.question("5").latest_value)
        else:
            seats = 0
            
        override_comments = smodels.CountryScorecardOverrideComments.objects.get(
            country=self.country, language__language=self.language )
        
        return {
            "commitments": [
                {"description": override_comments.cd2 or _("Signed Agreement"), "logo": self.gov_rating("1")},
                {"description": self.gov_comment("1"), "bullet": False}
            ],
            "health_sector":[
                {"description": _("Includes current targets and budgets"), "logo": self.gov_rating("2")},
                {"description": _("Jointly Assessed"), "logo": self.gov_rating("3")},
            ],
            "aid_effectiveness": [
                {"description": _("Active joint monitoring"), "logo": self.gov_rating("12")},
                {"description": _("Number of development partner missions"), "text": foz(self.gov_ltv("16"))},
                {"description": _("%(percentage)g%% of seats in the health sector coordination mechanism are allocated to civil society") % { 'percentage': (r2(seats*100)) }, "logo": cs_logo},
            ]
        }

    def get_health_finance(self):
        min_value = min([
                in_millions(foz(self.question("6").baseline_value)),
                in_millions(foz(self.question("6").latest_value)),
                in_millions(foz(self.question("7").baseline_value)),
                in_millions(foz(self.question("7").latest_value))
                ])
        if min_value < 10:
            r = r2
        else:
            r = r0
        
        domestic_baseline = r(in_millions(foz(self.question("6").baseline_value)))
        domestic_latest = r(in_millions(foz(self.question("6").latest_value)))
        all_baseline = r(in_millions(foz(self.question("7").baseline_value)))
        all_latest = r(in_millions(foz(self.question("7").latest_value)))

        external_baseline = all_baseline - domestic_baseline if all_baseline > domestic_baseline else 0
        external_latest = all_latest - domestic_latest if all_latest > domestic_latest else 0
        
        try:
            allocated_to_health = domestic_latest / r0(in_millions(foz(self.question("5").latest_value))) * 100
        except ZeroDivisionError:
            allocated_to_health = None

        increase = safe_diff(15, allocated_to_health)

        return {
            "total": {
                "series": [
                    {
                        "name": self.question("6").baseline_year, 
                        "domestic": domestic_baseline,
                        "external": external_baseline
                    },
                    get2010value(self.country, 'financing.health_finance'),
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

    def donor_capacity(self):
        qs = DPQuestion.objects.filter(
            submission__country=self.country, 
            submission__agency__in=self.country.agencies
        )
        agencytarget = AgencyTargets.objects.get(agency=None, indicator="2DPb")
        val = indicators.calc_indicator(qs, self.country, "2DPb")
        baseline = val[0][0]
        latest = val[0][2]

        rating = target.evaluate_indicator(agencytarget, baseline, latest)
        return rating_icon(rating)
        
    def get_systems(self):
        return {
            "management":{
                "header": _("REFLECTS GOOD PRACTICE (OR REFORM IN PROGRESS)"),
                "logo": rating_icon(self.ratings["5Ga"]["target"]),
                "description": _("Homines plous oinvorsei virei atque mulieres sacra ne quisquam ecise velet, neve inter ibei virei plous duobus, mulieribus plous tribus arfuise velent, nisei de praitoris urbani senatuosque sententiad, utei suprad scriptum est.")
            },

            "procurement": {
                "header": _("REFLECTS GOOD PRACTICE (OR REFORM IN PROGRESS)"),
                "logo": rating_icon(self.ratings["5Gb"]["target"]),
                "description": _("Homines plous oinvorsei virei atque mulieres sacra ne quisquam ecise velet, neve inter ibei virei plous duobus, mulieribus plous tribus arfuise velent, nisei de praitoris urbani senatuosque sententiad, utei suprad scriptum est.")
            },

            "technical": {
                "header": _("DONOR CAPACITY DEVELOPMENT PROVIDED THROUGH COORDINATED PROGRAMMES"),
                "logo": self.donor_capacity(),
                "description": _("Homines plous oinvorsei virei atque mulieres sacra ne quisquam ecise velet, neve inter ibei virei plous duobus, mulieribus plous tribus arfuise velent, nisei de praitoris urbani senatuosque sententiad, utei suprad scriptum est.")
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
        r8Gb = self.ratings["8Gb"]

        def progress_to_int(val):
            return {
                "y" : 2, "yy" : 2, 100 : 2,
                0 : 0, "n" : 0, None : 0, "nn" : 0,
                "yn" : 0,
            }[val]

        def cs_progress(val):
            if val == 4:
                return 2
            elif val > 0:
                return 1
            return 0

        base_targets = CountryTargets.objects.filter(country=None)
        def get_target(indicator):
            try:
                return CountryTargets.objects.get(indicator=indicator, country=self.country).tick_criterion_value
            except CountryTargets.DoesNotExist:
                return base_targets.get(indicator=indicator).tick_criterion_value

        return {
            "mutual_agreement":{
                "description": _("An IHP+ Compact or equivalent mutual agreement is in place."),
                "rating": rating_icon(r1G["target"]),
                "max": 2,
                "progress": add_previous_value(self.country, 'commitments.mutual_agreement', [
                    {"year": r1G["base_year"], "value":progress_to_int(r1G["base_val"])},
                    {"year": r1G["cur_year"], "value":progress_to_int(r1G["cur_val"])},
                ])
            },
            "health_plan":{
                "description": _("A National Health Sector Plan/ Strategy is in place with current targets & budgets that have been jointly assessed."),
                "rating": rating_icon(r2Ga["target"]),
                "max": 2,
                "progress": add_previous_value(self.country, 'commitments.health_plan', [
                    {"year": r2Ga["base_year"], "value":progress_to_int(r2Ga["base_val"])},
                    {"year": r2Ga["cur_year"], "value":progress_to_int(r2Ga["cur_val"])},
                ])
            },
            "hrh_plan":{
                "description": _("A costed, comprehensive national HRH plan (integrated with the health plan) is being implemented or developed."),
                "rating": rating_icon(r2Gb["target"]),
                "max": 2,
                "progress": add_previous_value(self.country, 'commitments.hrh_plan', [
                    {"year": r2Gb["base_year"], "value":progress_to_int(r2Gb["base_val"])},
                    {"year": r2Gb["cur_year"], "value":progress_to_int(r2Gb["cur_val"])},
                ])
            },
            "fundingcommitments":{
                "description": _("%(percentage)d%% (or an equivalent published target) of the national budget is allocated to health.") % { "percentage": round(get_target("3G")) },
                "rating": rating_icon(r3G["target"]),
                "progress": add_previous_value(self.country, 'commitments.fundingcommitments', [
                    {"year": r3G["base_year"], "value":foz(r3G["base_val"])},
                    {"year": r3G["cur_year"], "value":foz(r3G["cur_val"])},
                ]),
                "line": {"constant": round(get_target("3G"))},
                "max": 20
            },
            "health_funding":{
                "description": _("Halve the proportion of health sector funding not disbursed against the approved annual budget."),
                "rating": rating_icon(r4G["target"]),
                "progress": add_previous_value(self.country, 'commitments.health_funding', [
                    {"year": r4G["base_year"], "value":foz(r4G["base_val"])},
                    {"year": r4G["cur_year"], "value":foz(r4G["cur_val"])},
                ]),
                "max": 100
            },
            "cipa_scale":{
                "description": _("Improvement of at least one measure (ie 0.5 points) on the PFM/CPIA scale of performance."),
                "rating": rating_icon(r5Ga["target"]),
                "progress": add_previous_value(self.country, 'commitments.cipa_scale', [
                    {"year": r5Ga["base_year"], "value":foz(r5Ga["base_val"])},
                    {"year": r5Ga["cur_year"], "value":foz(r5Ga["cur_val"])},
                ]),
                "max": 5
            },
            "performance_scale":{
                "description": _("Improvement of at least one measure on the four-point scale used to assess performance for this sector."),
                "rating": rating_icon(r5Gb["target"]),
                "type":"dot",
                "progress": add_previous_value(self.country, 'commitments.performance_scale', [
                    {"year": r5Gb["base_year"], "value":r5Gb["base_val"]},
                    {"year": r5Gb["cur_year"], "value":r5Gb["cur_val"]},
                ])
            },

            "resources":{
                "description": _("A transparent and monitorable performance assessment framework is in place to assess progress in the health sector."),
                "rating": rating_icon(r6G["target"]),
                "max": 2,
                "progress": add_previous_value(self.country, 'commitments.resources', [
                    {"year": r6G["base_year"], "value":progress_to_int(r6G["base_val"])},
                    {"year": r6G["cur_year"], "value":progress_to_int(r6G["cur_val"])},
                ])
            },
            "accountability":{
                "description": _("Mutual assesments (such as joint Annual Health Sector Review) are being made of progress implementing commitments in the health sector, including on aid effectiveness."),
                "rating": rating_icon(r7G["target"]),
                "max": 2,
                "progress": add_previous_value(self.country, 'commitments.accountability', [
                    {"year": r7G["base_year"], "value":progress_to_int(r7G["base_val"])},
                    {"year": r7G["cur_year"], "value":progress_to_int(r7G["cur_val"])},
                ])
            },
            "civilsociety":{
                # The empty list here is required to get rid of the %%, whihch in turn
                # is required for translations to work. Removing it will cause a double
                # % on the scorecard.
                "description": _("At least 10%% of seats in the country's Health Sector Coordination mechanisms are allocated to Civil Society") % [],
                "rating": rating_icon(r8Gb["target"]),
                "max": 2,
                "progress": add_previous_value(self.country, 'commitments.civilsociety', [
                    {"year": r8G["base_year"], "value":cs_progress(foz(r8Gb["base_val"]))},
                    {"year": r8G["cur_year"], "value":cs_progress(foz(r8Gb["cur_val"]))},
                ])
            }
        }

