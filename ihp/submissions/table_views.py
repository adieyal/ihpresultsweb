from functools import partial
from collections import OrderedDict
import json
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404

import models
import target
import indicators
from indicators import NA_STR
import consts
import translations
import agency_scorecard

def foz(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0

def tbl_float_format(x, places=0):
    if type(x) == float:
        if places == 0:
            return int(round(x, places))
        else:
            return round(x, places) 
    elif x == NA_STR:
        return "N/A"
    elif x == None:
        return None
    return x

def perc_change(base_val, latest_val):
    none_vals = [None, NA_STR]
    if type(base_val) == str or type(latest_val) == str:
        return None
    if base_val in none_vals or latest_val in none_vals:
        return None
    if base_val == 0:
        return None
    return (latest_val - base_val) / base_val * 100.0

def agency_table_by_indicator(request, indicator, language="English", template_name="submissions/agency_table_by_indicator.html", extra_context=None):
    dp_gov_map = {
        "1DP" : "1G",
        "2DPa" : "2Ga",
        "2DPb" : "2Gb",
        "3DP" : "3G",
        "4DP" : "4G",
        "5DPa" : "5Gb",
        "5DPb" : "5Ga",
        "6DP" : "6G",
        "7DP" : "7G",
        "8DP" : "8G",
    }
    extra_context = extra_context or {} 
    extra_context["translation"] = request.translation

    country_calcs = None
    countries = models.Country.objects.all().order_by("country")
    if indicator in dp_gov_map:
        gov_indicator = dp_gov_map[indicator]
        country_calcs = [(c, target.calc_country_ratings(c)[gov_indicator]) for c in countries]
    
    agencies = []
    for agency in models.Agency.objects.all():
        agency_values = []
        for country in countries:
            if country in agency.countries:
                inds = indicators.calc_agency_country_indicators(agency, country, indicators.positive_funcs)
                ratings = target.country_agency_indicator_ratings(country, agency)

                base_val, base_year, latest_val, cur_year = inds[indicator][0]
                country_abs_values = {
                    "baseline_value" : tbl_float_format(base_val), 
                    "base_year" : base_year,
                    "latest_value" : tbl_float_format(latest_val), 
                    "cur_year" : cur_year,
                    "rating" : ratings[indicator],
                    "cellclass" : "",
                } 
            else:
                country_abs_values = {
                    "baseline_value" : "",
                    "base_year" : "",
                    "latest_value" : "",
                    "cur_year" : "",
                    "rating" : "",
                    "cellclass" : "notactive",
                } 
                
            agency_values.append((country, country_abs_values))
        agency_values = sorted(agency_values, key=lambda x: x[0].country)
        agencies.append((agency, agency_values))

    agencies = sorted(agencies, key=lambda x: x[0].agency)
    extra_context["agencies"] = agencies
    extra_context["countries"] = countries
    extra_context["country_calcs"] = country_calcs
    
    return direct_to_template(request, template=template_name, extra_context=extra_context)

def agency_table_by_agency(request, agency_id, language="English", template_name="submissions/agency_table.html", extra_context=None):
    extra_context = extra_context or {} 
    agency = get_object_or_404(models.Agency, pk=agency_id)

    extra_context["translation"] = translation = request.translation
    abs_values = OrderedDict()
    for country in agency.countries:
        country_abs_values = OrderedDict()
        inds = indicators.calc_agency_country_indicators(agency, country, indicators.positive_funcs)
        ratings = target.country_agency_indicator_ratings(country, agency)
        for indicator in inds:
            base_val, base_year, latest_val, latest_year = inds[indicator][0]
            country_abs_values[indicator] = {
                "base_val" : tbl_float_format(base_val), 
                "latest_val" : tbl_float_format(latest_val), 
                "perc_change" : tbl_float_format(perc_change(base_val, latest_val)),
                "base_year" : base_year,
                "latest_year" : latest_year,
                "rating" : ratings[indicator]
            } 
        abs_values[country.country] = country_abs_values
    extra_context["abs_values"] = sorted(abs_values.items())
    extra_context["spm_map"] = translation.spm_map
    extra_context["institution_name"] = translation.by_agency_title % agency.agency
    
    return direct_to_template(request, template=template_name, extra_context=extra_context)

def agency_volume_of_aid(request, indicator, template_name="submissions/agency_response_breakdown.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context["indicator"] = indicator

    return direct_to_template(request, template=template_name, extra_context=extra_context)

def agency_volume_of_aid_json(request, indicator):
    """
    View to calculate the volume of aid received
    Returns a json view with the following structure
    {
        "indicator" : "..." # indicator name
        "target" : "..."    # target value for a tick
        "countries" : [
            {
                "name" : "..."  # country name
                "possible_volume" : {
                    "value" : "..."   # sum of denominator values
                    "num_dps" : "..." # number of countries included
                    "countries" : "..." # countries included
                },
                "actual_volume" : {
                    "value" : "..."   # sum of numerator values (only including tick agencies)
                    "num_dps" : "..." # number of countries included
                    "countries" : "..." # countries included
                }
            }
        ]
    }
    """
    countries = models.Country.objects.order_by("country")
    try:
        _, args = indicators.indicator_funcs[indicator]
        arg1, arg2 = args
    except KeyError:
        raise Http404()

    denoms = models.DPQuestion.objects.filter(question_number=arg2) 
    def on_target_volume(country):
        total = 0
        count = 0
        agencies = []
        for agency in country.agencies:
            ratings = target.country_agency_indicator_ratings(country, agency)
            if ratings[indicator] == models.Rating.TICK:
                q = models.DPQuestion.objects.get(
                    submission__country=country, 
                    submission__agency=agency, 
                    question_number=arg1
                )
                agencies.append(agency)
                total += foz(q.cur_val)
        return total, agencies

    rating_target = models.AgencyTargets.objects.get(indicator=indicator, agency=None)
    
    on_targets = {}
    for c in countries:
        
        value, agencies = on_target_volume(c)
        on_targets[c] = {
            "value" : value,
            "num_dps" : len(agencies),
            "agencies" : agencies
        }

    fn_incl_agencies = lambda country : [
        s.submission.agency.agency 
        for s in denoms.filter(
            submission__country=c, 
            submission__agency__type="Agency"
        )
    ]


    targets = {
        "2DPa" : "85",
        "4DP" : "71",
    }

    js = {
        "indicator" : indicator,
        "target" : targets[indicator],
        "countries" : [
            {
                "name" : c.country,
                "possible_volume" : {
                    "value" : sum(foz(d.cur_val) for d in denoms.filter(submission__country=c)),
                    "num_dps" : len(fn_incl_agencies(c)),
                    "agencies" : fn_incl_agencies(c),
                },
                "actual_volume" : {
                    "value" : on_targets[c]["value"],
                    "num_dps" : on_targets[c]["num_dps"],
                    "agencies" : [a.agency for a in on_targets[c]["agencies"]]
                }
            }
            
        for c in countries]
    }

    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")


def agency_table_by_country(request, country_id, language="English", template_name="submissions/agency_table.html", extra_context=None):
    extra_context = extra_context or {} 
    country = get_object_or_404(models.Country, pk=country_id)

    extra_context["translation"] = translation = request.translation
    abs_values = OrderedDict()
    for agency in country.agencies:
        ratings = target.country_agency_indicator_ratings(country, agency)
        agency_abs_values = OrderedDict()
        inds = indicators.calc_agency_country_indicators(agency, country, indicators.positive_funcs)
        for indicator in inds:
            base_val, base_year, latest_val, latest_year = inds[indicator][0]
            agency_abs_values[indicator] = {
                "base_val" : tbl_float_format(base_val), 
                "latest_val" : tbl_float_format(latest_val), 
                "perc_change" : tbl_float_format(perc_change(base_val, latest_val)), 
                "base_year" : base_year,
                "latest_year" : latest_year,
                "rating" : ratings[indicator]
            } 
        abs_values[agency.agency] = agency_abs_values
    extra_context["abs_values"] = sorted(abs_values.items())
    extra_context["spm_map"] = translation.spm_map
    extra_context["institution_name"] = translation.by_country_title % country.country
    
    return direct_to_template(request, template=template_name, extra_context=extra_context)

def country_table(request, language="English", template_name="submissions/country_table.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context["translation"] = translation = request.translation
    abs_values = OrderedDict()
    for country in models.Country.objects.all().order_by("country"):
        country_abs_values = OrderedDict()
        country_ratings = target.calc_country_ratings(country)
        inds = indicators.calc_country_indicators(country, indicators.positive_funcs)
        for indicator in inds:
            tpl = inds[indicator][0]
            base_val, base_year, latest_val, latest_year = tpl
            rating = country_ratings[indicator]["target"]

            if type(base_val) == str: 
                base_val = base_val.upper()
            if type(latest_val) == str: 
                latest_val = latest_val.upper()
            if indicator == "2Ga":
                base_val1 = base_val[0] if base_val else None
                base_val2 = base_val[1] if base_val else None
                latest_val1 = latest_val[0] if latest_val else None
                latest_val2 = latest_val[1] if latest_val else None

                country_abs_values["2Ga1"] = (
                    tbl_float_format(base_val1), 
                    tbl_float_format(latest_val1), 
                    None,
                    base_year,
                    rating
                ) 
                country_abs_values["2Ga2"] = (
                    tbl_float_format(base_val2), 
                    tbl_float_format(latest_val2), 
                    None,
                    base_year,
                    rating,
                ) 
            elif indicator == "5Gb":
                country_abs_values["5Gb"] = (
                    base_val,
                    latest_val,
                    0,
                    base_year,
                    rating
                )
            else:
                decimal_places = {
                    "5Ga" : 1
                }
                places = decimal_places.get(indicator, 0)
                country_abs_values[indicator] = (
                    tbl_float_format(base_val, places), 
                    tbl_float_format(latest_val, places), 
                    tbl_float_format(perc_change(base_val, latest_val), places),
                    base_year,
                    rating
                ) 
        abs_values[country.country] = country_abs_values
    extra_context["abs_values"] = sorted(abs_values.items())
    extra_context["spm_map"] = translation.gov_spm_map
        
    return direct_to_template(request, template=template_name, extra_context=extra_context)
    
def agency_ratings(request, language="English", template_name="submissions/agency_ratings.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context["translation"] = translation = request.translation
    ratings = []
    data = dict([(agency, agency_scorecard.get_agency_scorecard_data(agency)) for agency in models.Agency.objects.all()])

    agencies = models.Agency.objects.all().order_by("agency")
    for indicator in indicators.dp_indicators:
        rating = OrderedDict()
        for agency in agencies:
            cur_val = data[agency][indicator]["cur_val"]
            base_val = data[agency][indicator]["base_val"]
            perc_change = ""
            try:
                cur_val = 100 - cur_val
                base_val = 100 - base_val
                perc_change = ((cur_val - base_val) / base_val) * 100
            except:
                pass

            rating[agency] = {
                "rating" : data[agency][indicator]["target"],
                "base_val" : base_val,
                "cur_val" : cur_val,
                "perc_change" : perc_change
            }
        ratings.append((indicator, rating, translation.spm_map[indicator]))
    
    extra_context["ratings"] = ratings
    extra_context["agencies"] = agencies
    return direct_to_template(request, template=template_name, extra_context=extra_context)

