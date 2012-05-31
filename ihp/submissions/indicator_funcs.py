from models import AgencyCountries, CountryExclusion, NotApplicable, Rating
from consts import NA_STR, MISSING
import json


base_selector = lambda q : q.baseline_value
cur_selector = lambda q : q.latest_value

def float_or_none(x):
    if NotApplicable.objects.is_not_applicable(x):
        return NA_STR
    try:
        return float(x)
    except:
        return None

def _sum_values(qs, selector):
    nas = [q for q in qs if float_or_none(selector(q)) == NA_STR]
    nones = [q for q in qs if float_or_none(selector(q)) == None]

    qs = [q for q in qs if float_or_none(selector(q)) not in [None, NA_STR]]
    if len(qs) == 0:
        return None if len(nones) > 0 else NA_STR
    
    return sum([float(selector(q)) for q in qs])

def count_factory(value):
    def count_value(qs, agency_or_country, selector, q):
        qs = [qq for qq in qs if qq.question_number==q]

        if len(qs) == 0:
            return 0

        if selector == base_selector:
            return len([q for q in qs if q.base_val.lower() == value.lower()])
        elif selector == cur_selector:
            return len([q for q in qs if q.cur_val.lower() == value.lower()])
    return count_value

def country_perc_factory(value):
    def perc_value(qs, agency, selector, q):
        # In some countries certain processes do not exists
        # the watchlist reduces the denominator if the agency
        # is active in such a country for a particular question

        count_value = count_factory(value)

        num_countries = float(len(qs))
        count = count_value(qs, agency, selector, q)
        return count / num_countries * 100 if num_countries > 0 else NA_STR

    return perc_value

def equals_or_zero(val):
    def test(qs, agency_or_country, selector, q):
        value = val.lower()
        
        qs = [qq for qq in qs if qq.question_number==q]
        try:
            assert len(qs) == 1
            
            if selector(qs[0]) == None:
                _val = 0
            else:
                _val = 100 if selector(qs[0]).lower() == value else 0

            return _val
        except AssertionError:
            return None
    return test

def equals_yes_or_no(val):
    def test(qs, agency_or_country, selector, q):
        value = val.lower()
        
        qs = [qq for qq in qs if qq.question_number==q]
        assert len(qs) == 1
        
        if selector(qs[0]) == None:
            _val = ""
        else:
            _val = "y" if selector(qs[0]).lower() == value else "n"

        return _val
    return test

def identity(qs, agency_or_country, selector, *args):
    return selector(qs[0])

def combine_yesnos(qs, agency_or_country, selector, *args):
    values = []
    for arg in args:
        qs1 = [q for q in qs if q.question_number==arg]

        if selector(qs1[0]) == None:
            val = " "
        else: 
            val = "y" if selector(qs1[0]).lower() == "yes" else "n"

        values.append(val)
    return "".join(values)

def calc_numdenom(qs, agency_or_country, selector, numq, denomq):
    den = _sum_values([q for q in qs if q.question_number==denomq], selector)
    num = _sum_values([q for q in qs if q.question_number==numq], selector)

    if den in [NA_STR, MISSING] or num in [NA_STR, MISSING]:
        return MISSING
    ratio = NA_STR
    if den > 0: ratio = num / den * 100
    return ratio

def calc_one_minus_numdenom(qs, agency_or_country, selector, numq, denomq):
    ratio = calc_numdenom(qs, agency_or_country, selector, numq, denomq)
    ratio = 100 - ratio if ratio not in [NA_STR, MISSING] else ratio
    return ratio

def sum_values(qs, agency_or_country, selector, *args):
    qs = [q for q in qs if q.question_number in args]
    return _sum_values(qs, selector)

