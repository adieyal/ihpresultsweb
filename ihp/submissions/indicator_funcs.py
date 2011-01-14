from models import AgencyCountries, Country8DPFix, CountryExclusion

base_selector = lambda q : q.baseline_value
cur_selector = lambda q : q.latest_value

def float_or_zero(val):
    try:
        return float(val)
    except: 
        return 0

def _sum_values(qs, selector):
    return sum([float_or_zero(selector(q)) for q in qs])
    
def func_8dpfix(qs, agency, selector, q):
    countries = Country8DPFix.objects.filter(agency=agency)
    denom = float(len(countries))
    if selector == base_selector:
        num = len([country for country in countries if country.baseline_progress])
    elif selector == cur_selector:
        num = len([country for country in countries if country.latest_progress])

    if denom > 0:
        return num / denom * 100
    else:
        return None

def count_factory(value):
    def count_value(qs, agency_or_country, selector, q):
        qs = qs.filter(
            question_number=q, 
        )

        if qs.count() == 0:
            return 0

        if selector == base_selector:
            return qs.filter(baseline_value__iexact=value).count()
        elif selector == cur_selector:
            return qs.filter(latest_value__iexact=value).count()
    return count_value

def country_perc_factory(value):
    def perc_value(qs, agency, selector, q):
        # In some countries certain processes do not exists
        # the watchlist reduces the denominator if the agency
        # is active in such a country for a particular question

        def calc_val(watchlist, val):
            countries = [
                country 
                for country in AgencyCountries.objects.get_agency_countries(agency) 
                if country not in watchlist
            ]
            
            num_countries = float(len(countries))
            return val / num_countries * 100 if num_countries > 0 else 0.0

        count_value = count_factory(value)
        if selector == base_selector:
            _value = count_value(
                qs.exclude(submission__country__country__in=CountryExclusion.objects.baseline_excluded_countries(q)),
                agency, selector, q
            )
            _value = calc_val(CountryExclusion.objects.baseline_excluded_countries(q), _value)

        elif selector == cur_selector:
            _value = count_value(
                qs.exclude(submission__country__country__in=CountryExclusion.objects.latest_excluded_countries(q)), 
                agency, selector, q
            )
            _value = calc_val(CountryExclusion.objects.latest_excluded_countries(q), _value)

        return _value
    return perc_value

def equals_or_zero(val):
    def test(qs, agency_or_country, selector, q):
        value = val.lower()
        
        qs = qs.filter(question_number=q)
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
        
        qs = qs.filter(question_number=q)
        assert len(qs) == 1
        
        if selector(qs[0]) == None:
            _val = ""
        else:
            _val = "y" if selector(qs[0]).lower() == value else "n"

        return _val
    return test

def combine_yesnos(qs, agency_or_country, selector, *args):
    values = []
    for arg in args:
        qs1 = qs.filter(question_number=arg)

        if selector(qs1[0]) == None:
            val = " "
        else: 
            val = "y" if selector(qs1[0]).lower() == "yes" else "n"

        values.append(val)
    return "".join(values)

def calc_numdenom(qs, agency_or_country, selector, numq, denomq):
    den = float(_sum_values(qs.filter(question_number=denomq), selector))
    num = float(_sum_values(qs.filter(question_number=numq), selector))

    ratio = None
    if den > 0: ratio = num / den * 100
    return ratio

def calc_one_minus_numdenom(qs, agency_or_country, selector, numq, denomq):
    ratio = calc_numdenom(qs, agency_or_country, selector, numq, denomq)
    ratio = 100 - ratio if ratio != None else None
    return ratio

def sum_values(qs, agency_or_country, selector, *args):
    qs = qs.filter(question_number__in=args)
    return float(_sum_values(qs, selector))
