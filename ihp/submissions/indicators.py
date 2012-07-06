from models import Submission, DPQuestion, AgencyCountries, GovQuestion, Country, NotApplicable, CountryExclusion, Agency
from indicator_funcs import *
import traceback
from utils import memoize
from consts import NA_STR, MISSING
from django.db.models.query import QuerySet
import logging

is_none = lambda x : x == None or (unicode(x)).strip() == ""
class IndicatorCalculator(object):
    def __init__(self, func, args, ignore_missing):
        self.func = func
        self.args = args 
        self.ignore_missing = ignore_missing

    def calc(self, qs, agency_or_country):
        countries = set(q.submission.country for q in qs)
        # TODO this will probably be super slow
        agency_countries = set((q.submission.agency, q.submission.country) for q in qs)
        questions = set(q.question_number for q in qs)

        excluded_countries = set()

        if not GovQuestion in set(type(q) for q in qs): # only exclude if this is a DP query
            # Get all the countries excluded from this indicator
            excluded_countries = reduce(
                lambda s1, s2: s1 | s2,  # union of two sets
                (set(self._excluded_countries(q)) for q in questions),  
                excluded_countries
            )


        excluded_countries = set(c for c in excluded_countries if c in countries)

        excluded_agency_countries = set((a, c) for (a, c) in agency_countries if c in excluded_countries)
        excluded_agency_countries |= set(
            (q.submission.agency, q.submission.country)
            for q in qs 
            if NotApplicable.objects.is_not_applicable(self._getvalue(q))
        )

        # If we no longer have any countries to check then return N/A
        if len(excluded_agency_countries) == len(agency_countries):
            return NA_STR

        remaining_qs = [
            q for q in qs 
            if not (q.submission.agency, q.submission.country) in excluded_agency_countries
        ]

        # Add any countries with a missing answer in one of their answers to the excluded list
        if self.ignore_missing:
            excluded_agency_countries |= set(
                (q.submission.agency, q.submission.country)
                for q in qs 
                if is_none(self._getvalue(q))
            )

            # If we no longer have any countries to check then return MISSING
            if len(excluded_agency_countries) == len(agency_countries):
                return MISSING

            remaining_qs = [
                q for q in qs 
                if not (q.submission.agency, q.submission.country) in excluded_agency_countries
            ]

            if len(remaining_qs) == 0:
                return MISSING
            
        val = self.func(remaining_qs, agency_or_country, self._selector, *self.args)
        return val

class BaselineIndicatorCalculator(IndicatorCalculator):
    def _getvalue(self, q):
        return q.base_val

    def _getyear(self, q):
        return q.baseline_year

    def _excluded_countries(self, qnum):
        return CountryExclusion.objects.baseline_excluded_countries(qnum)

    @property
    def _selector(self):
        return base_selector
        

class LatestIndicatorCalculator(IndicatorCalculator):
    def _getvalue(self, q):
        return q.cur_val

    def _getyear(self, q):
        return q.latest_year

    def _excluded_countries(self, qnum):
        return CountryExclusion.objects.latest_excluded_countries(qnum)

    @property
    def _selector(self):
        return cur_selector

def calc_indicator(qs, agency_or_country, indicator, funcs=None):
    is_none = lambda x : x == None or (unicode(x)).strip() == ""

    funcs = funcs or indicator_funcs
    func, args = funcs[indicator]
        
    qs2 = [q for q in qs if q.question_number in args]
    comments = [(question.question_number, question.submission.country, question.comments) for question in qs2]

    ignore_missing = True
    # For these indicators below it distorts the picture to exclude missing values from the denominator except where we are looking at the disaggregated level
    def is_disaggregated(qs):
        return len(set((q.submission.country, q.submission.agency) for q in qs)) == 1

    if indicator in ["1DP", "6DP", "7DP", "8DP"] and not is_disaggregated(qs):
        ignore_missing = False

    base_val = BaselineIndicatorCalculator(func, args, ignore_missing).calc(qs2, agency_or_country)
    
    cur_val = LatestIndicatorCalculator(func, args, ignore_missing).calc(qs2, agency_or_country)

    
    base_year = MISSING
    cur_year = MISSING
    if len(qs2) > 0:
        base_year = qs2[0].baseline_year
        cur_year = qs2[0].latest_year
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

    """
    indicators = ["2DPa", "2DPb", "2DPc", "3DP", "4DP", "5DPa", "5DPb", "5DPc"]
    qs = DPQuestion.objects.filter(submission__agency__type="Agency").select_related()

    results = [calc_indicator(qs, None, indicator, funcs) for indicator in indicators]
    return dict(zip(indicators, results))

def calc_agency_country_indicator(qs, agency, country, indicator, funcs=None):
    """
    Same as calc_agency_indicator above but only looks at a specific country
    """
    funcs = funcs or dict(indicator_funcs)
    try:
        funcs["1DP"] = (equals_or_zero("yes"), indicator_funcs["1DP"][1])
        funcs["6DP"] = (equals_or_zero("yes"), indicator_funcs["6DP"][1])
        funcs["7DP"] = (equals_or_zero("yes"), indicator_funcs["7DP"][1])
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
    "6G" , "7G", "8G", "8Gb",
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
    "4DP"  : (calc_numdenom, ("11old", "10old")),
    "5DPa" : (calc_one_minus_numdenom, ("11", "10")),
    "5DPb" : (calc_one_minus_numdenom, ("12", "2")),
    "5DPc" : (sum_values, ("13",)),
    "6DP"  : (country_perc_factory("yes"), ("14",)),
    "7DP"  : (country_perc_factory("yes"), ("15",)),
    "8DP"  : (country_perc_factory("yes"), ("16",)),
    "1G"   : (map_yes_no_under_development, ("1",)),
    "2Ga"  : (combine_yesnos, ("2", "3")),
    "2Gb"  : (map_yes_no_under_development, ("4",)),
    "3G"   : (calc_numdenom, ("6", "5")),
    "4G"   : (calc_one_minus_numdenom, ("8", "7")),
    "5Ga"  : (sum_values, ("9",)),
    "5Gb"  : (identity, ("10",)),
    "6G"  : (map_yes_no_under_development, ("11",)),
    "7G"  : (map_yes_no_under_development, ("12",)),
    "8G"   : (sum_values, ("13",)),
    "8Gb"  : (count_array, ("15",)),
    "Q2G" : (equals_yes_or_no("yes"), ("2",)),
    "Q3G" : (equals_yes_or_no("yes"), ("3",)),
    "Q12G" : (equals_yes_or_no("yes"), ("12",)),
    "Q21G" : (equals_yes_or_no("yes"), ("21",)),
}

# This data is duplicated above but the order is important above
# whereas it isn't here
indicator_questions = dict([
    (k, qs)
    for k, (_, qs) in indicator_funcs.items()
])

# Functions that calculate values in a positive sense - i.e. how much on budget, not how much off budget
positive_funcs = dict(indicator_funcs)
positive_funcs["2DPa"] = (calc_numdenom, indicator_funcs["2DPa"][1])
positive_funcs["4DP"] = indicator_funcs["4DP"]
positive_funcs["5DPa"] = (calc_numdenom, indicator_funcs["5DPa"][1])
positive_funcs["5DPb"] = (calc_numdenom, indicator_funcs["5DPb"][1])
positive_funcs["4G"] = (calc_numdenom, indicator_funcs["4G"][1])
