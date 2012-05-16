from models import Submission, DPQuestion, AgencyCountries, GovQuestion, Country, NotApplicable, CountryExclusion, Agency
from indicator_funcs import *
import traceback
from utils import memoize
from consts import NA_STR
from django.db.models.query import QuerySet
import logging

def calc_indicator(qs, agency_or_country, indicator, funcs=None):
    """
    Core function that calculates indicators. 

    qs - The set of questions to calculate the indicator from
    agency_or_country - The entity for which the indicator is being calculated for
    indicator - the indicator the is being calculated
    funcs - used to override the indicator functions
    """

    if type(qs) == QuerySet: qs = list(qs)
    is_none = lambda x : x == None or (unicode(x)).strip() == ""

    funcs = funcs or indicator_funcs
    func, args = funcs[indicator]
    
    qs2 = [q for q in qs if q.question_number in args]
    if indicator == "6DP" and qs[0].submission.country.country == "Sierra Leone":
        print qs2
        #import pdb; pdb.set_trace()
        #print qs2[0].baseline_value, qs2[1].baseline_value
        #print qs2[0].latest_value, qs2[1].latest_value
        print qs2[0].baseline_value
        print qs2[0].latest_value
    
    comments = [(question.question_number, question.submission.country, question.comments) for question in qs2]

    exclude_baseline = []
    exclude_latest = []
    baseline_questions = latest_questions = 0
    baseline_excluded_count = latest_excluded_count = 0
    
    for q in qs2:
        if type(q) == DPQuestion:
            baseline_not_excluded, latest_not_excluded = CountryExclusion.objects.is_applicable(q.question_number, q.submission.country)
            baseline_excluded = not baseline_not_excluded
            latest_excluded = not latest_not_excluded
        else:
            baseline_excluded, latest_excluded = False, False

        if NotApplicable.objects.is_not_applicable(q.base_val) or baseline_excluded or is_none(q.base_val):
            exclude_baseline.append(q.submission.id)
        if NotApplicable.objects.is_not_applicable(q.cur_val) or latest_excluded or is_none(q.cur_val):
            exclude_latest.append(q.submission.id)
        if is_none(q.base_val): baseline_questions += 1
        if is_none(q.cur_val): latest_questions += 1
        if baseline_excluded: baseline_excluded_count += 1
        if latest_excluded: latest_excluded_count += 1
        # TODO - need to do something about the 8DPFix - is_none does not cater for it

    qs2_baseline = [q for q in qs2 if not q.submission.id in exclude_baseline]
    qs2_latest = [q for q in qs2 if not q.submission.id in exclude_latest]

    if len(qs2_baseline) == 0:
        if baseline_excluded_count == len(qs2):
            base_val = NA_STR
        elif baseline_questions > 0:
            base_val = None
        else:
            base_val = NA_STR
    else:
        base_val = func(qs2_baseline, agency_or_country, base_selector, *args)
        if base_val == NA_STR and baseline_questions > 0:
            base_val = None

    if len(qs2_latest) == 0:
        if latest_excluded_count == len(qs2):
            cur_val = NA_STR
        elif latest_questions > 0:
            cur_val = None
        else:
            cur_val = NA_STR
    else:
        cur_val = func(qs2_latest, agency_or_country, cur_selector, *args)
        if cur_val == NA_STR and latest_questions > 0:
            cur_val = None
        
    # TODO here i assume that the year is the same across all years and all questions. 
    if len(qs2) > 0: 
        cur_year = qs2[0].latest_year
        base_year = qs2[0].baseline_year
    else:
        cur_year = base_year = None

    return (base_val, base_year, cur_val, cur_year), comments

def calc_agency_indicator(qs, agency, indicator):
    """
    Calculate the value of a particular indicator for the given agency
    Returns a tuple ((base_val, base_year, cur_val, cur_year), indicator comment)
    """
    return calc_indicator(qs, agency, indicator)

def calc_agency_indicators(agency):
    """
    Calculates all the indicators for the given agency
    Returns a dict with the following form
    {
        "1DP" : ((base_1dp, base_1dp_year, cur_1dp, cur_1dp_year), comment_1dp),
        "2DPa" : ((base_2dpa, base_2dpa_year, cur_2dpa, cur_2dpa_year), comment_2dp),
        .
        .
        .
    }
    """
    qs = DPQuestion.objects.filter(submission__agency=agency, submission__country__in=agency.countries).select_related()
    results = [calc_agency_indicator(qs, agency, indicator) for indicator in dp_indicators]
    return dict(zip(dp_indicators, results))

def calc_overall_agency_indicators(funcs=None):
    """
    Calculates all indicators aggregated across all agencies and agencycountries
    i.e. there will be two values per indicator, baseline value and latest value
    currently only calculating for 2DPa, 2DPb, 2DPc, 3DP, 5DPa, 5DPb, 5DPc

    2008 base years are excluded

    """
    indicators = ["2DPa", "2DPb", "2DPc", "3DP", "4DP", "5DPa", "5DPb", "5DPc"]
    qs = DPQuestion.objects.filter(submission__agency__type="Agency").exclude(baseline_year="2008").select_related()

    results = [calc_indicator(qs, None, indicator, funcs) for indicator in indicators]
    return dict(zip(indicators, results))

def calc_agency_country_indicator(qs, agency, country, indicator, funcs=None):
    """
    Same as calc_agency_indicator above but only looks at a specific country
    """
    funcs = funcs or dict(indicator_funcs)
    try:
        funcs["1DP"] = (equals_or_zero("yes"), ("1",))
        funcs["6DP"] = (equals_or_zero("yes"), ("14",))
        funcs["7DP"] = (equals_or_zero("yes"), ("15",))
        return calc_indicator(qs, agency, indicator, funcs)
    except:
        traceback.print_exc()
        

def calc_agency_country_indicators(agency, country, funcs=None):
    """
    Same as calc_agency_indicators above but only looks at a specific country
    """
    qs = list(DPQuestion.objects.filter(submission__agency=agency, submission__country=country).select_related())
    results = [calc_agency_country_indicator(qs, agency, country, indicator, funcs) for indicator in dp_indicators]
    return dict(zip(dp_indicators, results))

def calc_country_indicator(qs, country, indicator, funcs=None):
    """
    Calculate the value of a particular indicator for the given country
    Returns a tuple ((base_val, base_year, cur_val, cur_year), indicator comment)
    """
    return calc_indicator(qs, country, indicator, funcs)

def calc_country_indicators(country, funcs=None):
    """
    Calculates all the indicators for the given country
    Returns a dict with the following form
    {
        "1G" : ((base_1g, base_1g_year, cur_1g, cur_1g_year), comment_1g),
        "2Ga" : ((base_2ga, base_2ga_year, cur_2ga, cur_2ga_year), comment_2g),
        .
        .
        .
    }
    """
    qs = GovQuestion.objects.filter(submission__country=country).select_related()
    results = [calc_country_indicator(qs, country, indicator, funcs) for indicator in g_indicators]
    return dict(zip(g_indicators, results))

def calc_country_agency_indicator(qs, country, agency, indicator, funcs=None):
    """
    Same as calc_country_indicator above but only looks at a specific agency
    """
    funcs = funcs or dict(indicator_funcs)
    return calc_indicator(qs, country, indicator, funcs)

def calc_country_agency_indicators(country, agency, funcs=None):
    """
    Same as calc_agency_indicators above but only looks at a specific country
    """
    qs = list(GovQuestion.objects.filter(submission__agency=agency, submission__country=country).select_related())
    logging.error("qs = %s" % qs)
    results = [calc_country_agency_indicator(qs, country, agency, indicator, funcs) for indicator in g_indicators]
    return dict(zip(g_indicators, results))

dp_indicators = [
    "1DP" , "2DPa", "2DPb",
    "2DPc", "3DP" , "4DP" ,
    "5DPa", "5DPb", "5DPc",
    "6DP" , "7DP" , "8DP" ,
]

g_indicators = [
    "1G" , "2Ga", "2Gb",
    "3G" , "4G", "5Ga", "5Gb",
    "6G" , "7G", "8G",
    "Q2G", "Q3G",
    "Q12G", "Q21G",
]

#TODO do checks to ensure that questions that aren't answered to break anything
indicator_funcs = {
    "1DP"  : (country_perc_factory("yes"), ("1",)),
    "2DPa" : (calc_one_minus_numdenom, ("3", "2")),
    "2DPb" : (calc_numdenom, ("5", "4")),
    "2DPc" : (calc_numdenom, ("7", "6")),
    "3DP"  : (calc_numdenom, ("8", "6")),
    "4DP"  : (calc_numdenom, ("6", "9")),
    "5DPa" : (calc_one_minus_numdenom, ("11", "10")),
    "5DPb" : (calc_one_minus_numdenom, ("12", "2")),
    "5DPc" : (sum_values, ("13",)),
    "6DP"  : (country_perc_factory("yes"), ("14",)),
    "7DP"  : (country_perc_factory("yes"), ("15",)),
    "8DP"  : (func_8dpfix, ("16",)),
    "1G"   : (equals_yes_or_no("yes"), ("1",)),
    "2Ga"  : (combine_yesnos, ("2", "3")),
    "2Gb"  : (equals_or_zero("yes"), ("4",)),
    "3G"   : (calc_numdenom, ("6", "5")),
    "4G"   : (calc_one_minus_numdenom, ("8", "7")),
    "5Ga"  : (sum_values, ("9",)),
    "5Gb"  : (sum_values, ("10",)),
    "6G"   : (equals_yes_or_no("yes"), ("11",)),
    "7G"   : (equals_yes_or_no("yes"), ("12",)),
    "8G"   : (calc_numdenom, ("13", "14")),
    "Q2G" : (equals_yes_or_no("yes"), ("2",)),
    "Q3G" : (equals_yes_or_no("yes"), ("3",)),
    "Q12G" : (equals_yes_or_no("yes"), ("12",)),
    "Q21G" : (equals_yes_or_no("yes"), ("21",)),
}

# This data is duplicated above but the order is important above
# whereas it isn't here
indicator_questions = {
    "1DP"  : ("1",),
    "2DPa" : ("2", "3"),
    "2DPb" : ("4", "5"),
    "2DPc" : ("6", "7"),
    "3DP"  : ("6", "8"),
    "4DP"  : ("6", "9"),
    "5DPa" : ("10", "11"),
    "5DPb" : ("2", "12"),
    "5DPc" : ("13",),
    "6DP"  : ("14",),
    "7DP"  : ("15",),
    "8DP"  : ("16",),
    "1G"   : ("1",),
    "2Ga"  : ("2", "3"),
    "2Gb"  : ("4",),
    "3G"   : ("6", "5"),
    "4G"   : ("8", "7"),
    "5Ga"  : ("9",),
    "5Gb"  : ("10",),
    "6G"   : ("11",),
    "7G"   : ("12",),
    "8G"   : ("13", "14"),
    "Q2G" : ("2",),
    "Q3G" : ("3",),
    "Q12G" : ("12",),
    "Q21G" : ("21",),
}

# Functions that calculate values in a positive sense - i.e. how much on budget, not how much off budget
positive_funcs = dict(indicator_funcs)
positive_funcs["2DPa"] = (calc_numdenom, ("3", "2"))
positive_funcs["4DP"] = (calc_numdenom, ("9", "6"))
positive_funcs["5DPa"] = (calc_numdenom, ("11", "10"))
positive_funcs["5DPb"] = (calc_numdenom, ("12", "2"))
positive_funcs["4G"] = (calc_numdenom, ("8", "7"))
