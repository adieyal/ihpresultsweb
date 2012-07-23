import json
import models
import indicators
import target
from functools import partial

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def foz(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0

def dfid_2dpa(request):
    agency = get_object_or_404(models.Agency, agency="UK")
    first_wave = ["Burundi", "Cambodia", "Ethiopia", "Kenya", "Mali", "Mozambique", "Nepal", "Zambia"]

    all_results = indicators.calc_agency_indicator(
        models.DPQuestion.objects.filter(
            submission__agency=agency, submission__country__in=agency.countries
        ),
        agency, "2DPa", funcs=indicators.positive_funcs
    )[0]

    first_wave_results = indicators.calc_agency_indicator(
        models.DPQuestion.objects.filter(
            submission__agency=agency, submission__country__country__in=first_wave
        ),
        agency, "2DPa", funcs=indicators.positive_funcs
    )[0]
    
    js = {
        "all" : {
            "num_countries" : len(agency.countries),
            "baseline" : all_results[0],
            "latest" : all_results[2],
        },
        "first_wave" : {
            "num_countries" : len(first_wave),
            "baseline" : first_wave_results[0],
            "latest" : first_wave_results[2],
        },
    }

    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def all_indicators(request, agency_id):
    agency = get_object_or_404(models.Agency, pk=agency_id)
    results = indicators.calc_agency_indicators(agency, funcs=indicators.positive_funcs) 
    with models.old_dataset():
        results_2009 = indicators.calc_agency_indicators(agency, funcs=indicators.positive_funcs) 
    
    js = [
        {
            "indicator" : indicator,
            "baseline" : foz(result[0][0]),
            "2009" : foz(results_2009[indicator][0][2]),
            "latest" : foz(result[0][2]),
        } 
        for (indicator, result) in results.items()
    ]

    js = sorted(js, key=lambda x : x["indicator"])
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def country_by_indicator(request, indicator):
    countries = models.Country.objects.order_by("country")
    
    js = []
    for country in countries:
        res = indicators.calc_agency_indicator_by_country(country, indicator, indicators.positive_funcs)[0]
        with models.old_dataset():
            res_2009 = indicators.calc_agency_indicator_by_country(country, indicator, indicators.positive_funcs)[0]
        js.append({
            "country" : country.country,
            "data" : {
                "baseline" : foz(res[0]),
                "2009" : foz(res_2009[2]),
                "latest" : foz(res[2]),
            }
        })
            
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def hss(request):
    countries = models.Country.objects.order_by("country")
    
    js = []
    for country in countries:
        js.append({
            
            "country" : country.country,
            "phc_clincs" : country.normalise_by_population(country.phc_clinics),
            "health_workers" : country.normalise_by_population(country.health_workers),
            "health_systems" : country.funds_for_health_systems
        })
            
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def health_budget(request):
    countries = models.Country.objects.order_by("country")
    
    js = []
    for country in countries:
        qs = models.GovQuestion.objects.filter(submission__country=country).select_related()

        res = indicators.calc_country_indicator(qs, country, "3G", funcs=indicators.positive_funcs)[0]

        with models.old_dataset():
            qs_2009 = models.GovQuestion.objects.filter(submission__country=country).select_related()
            res_2009 = indicators.calc_country_indicator(qs_2009, country, "3G", funcs=indicators.positive_funcs)[0]

        js.append({
            "country" : country.country,
            "budget" : {
                "baseline" : res[0],
                "2009" : foz(res_2009[2]),
                "latest" : res[2],
            }
        })
            
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def budget_disbursement(request):
    countries = models.Country.objects.order_by("country")
    
    js = []
    for country in countries:
        qs = models.GovQuestion.objects.filter(submission__country=country).select_related()

        res = indicators.calc_country_indicator(qs, country, "4G", funcs=indicators.positive_funcs)[0]

        with models.old_dataset():
            qs_2009 = models.GovQuestion.objects.filter(submission__country=country).select_related()
            res_2009 = indicators.calc_country_indicator(qs_2009, country, "4G", funcs=indicators.positive_funcs)[0]

        js.append({
            "country" : country.country,
            "budget" : {
                "baseline" : res[0],
                "2009" : foz(res_2009[2]),
                "latest" : res[2],
            }
        })
            
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def volumes_by_country(request):
    countries = models.Country.objects.order_by("country")
    agencies = models.Agency.objects.order_by("agency")
    qs = models.DPQuestion.objects.filter(question_number=6)

    js = []
    for agency in agencies:
        countries_arr = []
        for country in countries:
            try:
                aid = qs.get(submission__agency=agency, submission__country=country).cur_val
                aid = float(aid)
            except models.DPQuestion.DoesNotExist:
                aid = 0 
            except (ValueError, TypeError):
                aid = 0
            countries_arr.append({
                "name" : country.country,
                "value" : aid
            })
        js.append({
            "agency" : agency.agency,
            "countries" : countries_arr
        })
            
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def fragile_states(request, language=None):
    fragile_states = ["Burundi", "DRC", "Nepal", "Sierra Leone", "Sudan", "Togo"]
    fragile_countries = models.Country.objects.filter(country__in=fragile_states)
    non_fragile_countries = models.Country.objects.exclude(country__in=fragile_states)
    fragile_indicators = ["2DPa", "2DPc", "3DP", "4DP", "5DPb"]

    def slice_data(countries):
        calculator = partial(indicators.calc_indicator, agency_or_country=None, funcs=indicators.positive_funcs)
        return [
            {
                "indicator" : indicator, 
                "value" : calculator(
                    models.DPQuestion.objects.filter(submission__country__in=countries),
                    indicator=indicator
                )[0][2],
            }
            for indicator in fragile_indicators
        ]

    js = {
        "fragile_states" : {
            "countries" : [c.country for c in fragile_countries],
            "indicators" : slice_data(fragile_countries)
        },
        "non_fragile_states" : {
            "countries" : [c.country for c in non_fragile_countries],
            "indicators" : slice_data(non_fragile_countries)
        }
    }
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def two_by_two_analysis(request):

    all_ratings = {}
    countries = models.Country.objects.all()

    has_all_indicators = lambda r : (
        r["1G"]["target"] == models.Rating.TICK
        and r["2Ga"]["target"] == models.Rating.TICK
        and r["6G"]["target"] == models.Rating.TICK
        and r["7G"]["target"] == models.Rating.TICK
    )

    has_strong_pfm = lambda r : foz(r["5Ga"]["cur_val"]) >= 3.5
    has_weak_pfm = lambda r : not has_strong_pfm(r)
    get_country = lambda r : r["1G"]["country_name"]

    all_ratings = [target.calc_country_ratings(c) for c in countries]
    all_indicators = set(map(get_country, filter(has_all_indicators, all_ratings)))
    not_all_indicators = set(map(get_country, filter(lambda x : not has_all_indicators(x), all_ratings)))
    strong_pfm = set(map(get_country, filter(has_strong_pfm, all_ratings)))
    weak_pfm = set(map(get_country, filter(has_weak_pfm, all_ratings)))

    allstrong = all_indicators & strong_pfm
    allweak = all_indicators & weak_pfm
    notallstrong = not_all_indicators & strong_pfm
    notallweak = not_all_indicators & weak_pfm

    def indicator_dict(indicator):
        calculator = partial(indicators.calc_indicator, indicator=indicator, agency_or_country=None, funcs=indicators.positive_funcs)

        def slice_data(countries):
            return {
                "value" : calculator(models.DPQuestion.objects.filter(submission__country__in=countries))[0][2],
                "num_countries" : len(countries),
                "countries" : [c.country for c in countries],
            }
        
        return {
            "indicator" : indicator,
            "allstrong" : slice_data(allstrong),
            "allweak" : slice_data(allweak),
            "notallstrong" : slice_data(notallstrong),
            "notallweak" : slice_data(notallweak),
            "all_indicators" : slice_data(all_indicators),
            "not_all_indicators" : slice_data(not_all_indicators),
            "strong_pfm" : slice_data(strong_pfm),
            "weak_pfm" : slice_data(weak_pfm),
        }

    js = {
        "indicators" : [
            indicator_dict("2DPa"),
            indicator_dict("2DPc"), 
            indicator_dict("3DP"), 
            indicator_dict("4DP"), 
        ]
    }
    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def top5_countries(request):
    top3 = models.Country.objects.filter(country__in=["Ethiopia", "Mali", "Mozambique"])
    next2 = models.Country.objects.filter(country__in=["Niger", "Uganda"])

    fn_names = lambda countries : [c.country for c in countries]
    the_rest = models.Country.objects.exclude(country__in=fn_names(top3)).exclude(country__in=fn_names(next2))

    calculator = partial(indicators.calc_indicator, agency_or_country=None, funcs=indicators.positive_funcs)
    calc_indicators = ["2DPa", "2DPc", "3DP", "4DP", "5DPb"]

    js = {
        "top3" : [],
        "next2" : [],
        "the_rest" : []
    }

    def fn_country_values(country, indicator):
        calculation = calculator(
            models.DPQuestion.objects.filter(submission__country=country), 
            indicator=indicator
        )
        with models.old_dataset():
            old_calculation = calculator(
                models.DPQuestion.objects.filter(submission__country=country),
                indicator=indicator
            )

        return {
            "name" : c.country,
            "2007" : calculation[0][0],
            "2009" : old_calculation[0][2],
            "2011" : calculation[0][2],
        }

    for indicator in calc_indicators:
        for label, subset in [("top3", top3), ("next2", next2), ("the_rest", the_rest)]:
            calculation = calculator(
                models.DPQuestion.objects.filter(submission__country__in=subset), indicator=indicator
            )

            with models.old_dataset():
                old_calculation = calculator(
                    models.DPQuestion.objects.filter(submission__country__in=subset), indicator=indicator
                )


            js[label].append({
                "indicator" : indicator,
                "averages" : {
                    "2007" : calculation[0][0],
                    "2009" : old_calculation[0][2],
                    "2011" : calculation[0][2],
                },
                "by_country" : [fn_country_values(c, indicator) for c in subset]
            })

    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")

def early_signatories(request):
    top3 = models.Country.objects.filter(country__in=["Ethiopia", "Mali", "Mozambique", "Nepal"])
    next2 = models.Country.objects.filter(country__in=["Burundi"])

    fn_names = lambda countries : [c.country for c in countries]

    calculator = partial(indicators.calc_indicator, agency_or_country=None, funcs=indicators.positive_funcs)
    calc_indicators = ["2DPa", "3DP", "4DP", "5DPb"]

    js = {
        "top3" : [],
        "next2" : [],
    }

    def fn_country_values(country, indicator):
        calculation = calculator(
            models.DPQuestion.objects.filter(submission__country=country), 
            indicator=indicator
        )
        with models.old_dataset():
            old_calculation = calculator(
                models.DPQuestion.objects.filter(submission__country=country),
                indicator=indicator
            )

        return {
            "name" : c.country,
            "2007" : calculation[0][0],
            "2009" : old_calculation[0][2],
            "2011" : calculation[0][2],
        }

    for indicator in calc_indicators:
        for label, subset in [("top3", top3), ("next2", next2)]:
            calculation = calculator(
                models.DPQuestion.objects.filter(submission__country__in=subset), indicator=indicator
            )

            with models.old_dataset():
                old_calculation = calculator(
                    models.DPQuestion.objects.filter(submission__country__in=subset), indicator=indicator
                )


            js[label].append({
                "indicator" : indicator,
                "averages" : {
                    "2007" : calculation[0][0],
                    "2009" : old_calculation[0][2],
                    "2011" : calculation[0][2],
                },
                "by_country" : [fn_country_values(c, indicator) for c in subset]
            })

    return HttpResponse(json.dumps(js, indent=4), mimetype="application/json")
