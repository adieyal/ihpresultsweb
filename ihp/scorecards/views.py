# Create your views here.
from django.shortcuts import get_object_or_404
from submissions.models import Agency, AgencyProfile, Language
from submissions.target import calc_agency_ratings, dp_indicators
import json
import string
from django.views.generic.simple import direct_to_template


def json_scorecard_by_agency(agency_id, language):
    """
    json dump of scorecard data takes agency and language
    """
    agency = get_object_or_404(Agency, id=agency_id)
    language = get_object_or_404(Language, language=language)
    profile = get_object_or_404(AgencyProfile, agency=agency,
                                language=language)

    data = calc_agency_ratings(agency, language)

    a = {'agency':
                {
                 'name': agency.agency,
                 'profile': profile.description,
                 'logo_url': '/media/flags/%s.png' %
                 string.replace(string.lower(agency.agency), " ", "."),
                 'active_countries': [{'name':x.country,
                               'logo_url': '/media/flags/%s.png' %
                            string.replace(string.lower(x.country), " ", ".")}
                              for x in agency.countries]
                 },
         'overall_progress': dict(zip(dp_indicators,
                                [{"target": data[indicator]["target_val"],
                                   "baseline": data[indicator]["base_val"],
                                   "height":50,
                                "data":[{"key":data[indicator]["base_year"],
                                         "value":data[indicator]['base_val']},
                                         {"key":data[indicator]["cur_year"],
                                          "value":data[indicator]['cur_val']},
                                         ]}
                                for indicator in dp_indicators])),
         'ratings': dict(zip(dp_indicators, ['/media/icons/%s.svg' %
            data[indicator]['target']  for indicator in dp_indicators])),
         'additional_information':  dict(zip(dp_indicators,
            [data[indicator]["commentary"] for indicator in dp_indicators]))
        }

    r = json.dumps(a, indent=2)
    #print r
    return r


def export_dp_agency_scorecard(request,
        agency_id,
        language,
        template_name="index.html",
        extra_context=None):
    """
    View that exports scorecard data of agency as json
    """
    extra_context = extra_context or {}
    extra_context["agency_scorecard"] = json_scorecard_by_agency(agency_id,
                                                                language)

    return direct_to_template(request, template=template_name,
                            extra_context=extra_context)
