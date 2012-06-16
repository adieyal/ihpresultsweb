# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from submissions.models import Agency, AgencyProfile, Language, DPScorecardSummary, Country, AgencyCountries, GovQuestion
from submissions.target import calc_agency_ratings, dp_indicators
import json
import string
from django.views.generic.simple import direct_to_template
from django.conf import settings
from models import GovScorecard

def dp_scorecard_json(request, agency_id, language):
    """
    json dump of scorecard data takes agency and language
    """

    def normalise_name(v):
        return v.lower().replace(" ", ".")

    agency = get_object_or_404(Agency, id=agency_id)
    language = get_object_or_404(Language, language=language)
    profile = get_object_or_404(
        AgencyProfile, agency=agency,
        language=language
    )
    summary = get_object_or_404(DPScorecardSummary, agency=agency, language=language)

    data = calc_agency_ratings(agency, language)

    # TODO - ugly hack to return the correct target values
    for indicator in dp_indicators:
        if data[indicator]["target_val"] != round(data[indicator]["target_val"]):
            data[indicator]["target_val"] += 0.5

        if indicator in ["2DPa", "5DPa", "5DPb"]:
            if "one_minus_base_val" in data[indicator]:
                data[indicator]["base_val"] = data[indicator]["one_minus_base_val"]
            if "one_minus_cur_val" in data[indicator]:
                data[indicator]["cur_val"] = data[indicator]["one_minus_cur_val"]

        if indicator in ["2DPa"]:
            data[indicator]["target_val"] = 85

        if indicator in ["5DPa", "5DPb"]:
            data[indicator]["target_val"] = 80

        if indicator in ["5DPc"]:
            data[indicator]["target_val"] = ""
            

    a = {
        'agency': {
            'name': agency.agency,
            'profile': profile.description,
            'logo_url': '/media/logos/%s.png' % normalise_name(agency.agency),
            'active_countries': [
                {
                    'name':x.country,
                    'logo_url': '/media/flags/%s.png' % normalise_name(x.country)
                } 
                for x in agency.countries
            ]
        },
        'overall_progress': dict(
            zip(dp_indicators, [
                {
                    "target" : data[indicator]["target_val"],
                    "baseline" : data[indicator]["base_val"],
                    "height" : 50,
                    "data" : [
                        {
                            "key" : data[indicator]["base_year"],
                            "value" : data[indicator]['base_val']
                        },
                        {   
                            "key":data[indicator]["cur_year"],
                            "value":data[indicator]['cur_val']
                        },
                    ]
                }
                for indicator in dp_indicators
            ])
        ),
        'ratings' : dict(
            zip(dp_indicators, [
                '/media/icons/%s.svg' % data[indicator]['target']  
                for indicator in dp_indicators
            ])
        ),
        'additional_information':  dict(
            zip(dp_indicators, [
                data[indicator]["commentary"] 
                for indicator in dp_indicators
            ])
        ),
        'summary' : {
            "erb1" : summary.erb1,
            "erb2" : summary.erb2,
            "erb3" : summary.erb3,
            "erb4" : summary.erb4,
            "erb5" : summary.erb5,
            "erb6" : summary.erb6,
            "erb7" : summary.erb7,
            "erb8" : summary.erb8,
        },
    }

    r = json.dumps(a, indent=4)
    return HttpResponse(r)

def dp_scorecard(request, agency_id, language, template_name="scorecards/dp.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context.update({
        "agency_id" : agency_id,
        "language" : language,
    })

    return direct_to_template(
        request, template=template_name,
        extra_context=extra_context
    )

def gov_scorecard_json(request, country_id, language):
    """
    json dump of scorecard data takes country and language
    """

    country = get_object_or_404(Country, id=country_id)
    gov_scorecard = GovScorecard(country) 
    media_url = settings.MEDIA_URL
    agencies = AgencyCountries.objects.get_country_agencies(country)
    def foz(x):
        try:
            return float(x)
        except:
            return 0

    r0 = lambda x : round(float(x), 0)

    country_flag = lambda country : "%sflags/%s.png" % (media_url, country.lower())
    agency_logo = lambda agency : "%slogos/%s.png" % (media_url, agency.lower())
    rating_icon = lambda icon : "%sicons/%s.svg" % (media_url, icon)
    answers = {
        "yes" : "tick",
        True : "tick",
        "no" : "cross",
        False : "cross",
        "under_development" : "cross",
        "" : "line",
    }
    submission = GovQuestion.objects.get(question_number=1, submission__country=country).submission
    gov_ltv = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).latest_value
    gov_lty = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).latest_year
    gov_blv = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).baseline_value
    gov_bly = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).baseline_year
    gov_comment = lambda qnum : GovQuestion.objects.get(question_number=qnum, submission=submission).comments
    gov_rating = lambda qnum : rating_icon(answers[gov_ltv(qnum)])
    a = {
        "info": {
            "country": country.country.upper(),
            "flag": country_flag(country.country)
        },

        "managing_results":{
            "national_results": gov_rating("11"),
            "functional_health": gov_rating("22"),
            "decisons_results": gov_rating("11"),
            "joint_health": gov_rating("12"),
        },
        "countries": [agency_logo(agency.agency) for agency in agencies],
        "health_systems": gov_scorecard.get_health_systems(),

        "country_ownership":{
            "commitments": [
                {"description": "Signed Agreement", "logo": gov_rating("1")},
                {"description": gov_comment("1"), "bullet": False}
            ],
            "health_sector":[
                {"description": "Includes current targets and budgets", "logo": gov_rating("2")},
                {"description": "Jointly Assessed", "logo": gov_rating("3")},
            ],
            "aid_effectiveness": [
                {"description": "Active joint monitoring", "logo": gov_rating("12")},
                {"description": "Number of development partner missions", "text": float(gov_ltv("16"))},
                {"description": "10% of seats in the health sector coordination mechanism are allocated to civil society", "logo": rating_icon(answers[foz(gov_ltv("13")) >= 10])},
                {"description": "", "logo": "icons/tick.svg", "bullet" : False}
            ]
        },

        "health_finance": gov_scorecard.get_health_finance(),
        "systems": gov_scorecard.get_systems(),
        "progress": gov_scorecard.get_mdg_progress(),
        "commitments" : gov_scorecard.get_ratings(),
    }
    r = json.dumps(a, indent=4)
    return HttpResponse(r, mimetype="application/json")

def gov_scorecard(request, country_id, language, template_name="scorecards/gov.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context.update({
        "country_id" : country_id,
        "language" : language,
    })

    return direct_to_template(
        request, template=template_name,
        extra_context=extra_context
    )
