from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('ihp.submissions.graphs',
    url(r"^agencies/highlevel/(?P<language>\w+)/$", "highlevelgraphs", name="highlevelgraphs"),
    url(r"^agencies/projection/(?P<language>\w+)/$", "projectiongraphs", name="projectiongraphs"),
    url(
        r"^agencies/(?P<indicator>\w+)/(?P<language>\w+)/$", 
        "agency_graphs_by_indicator", 
        name="agency_graphs_by_indicator"
    ),
    url(r"^agencies/(?P<agency_name>[a-zA-Z\s]+)/(?P<language>\w+)/$", "agencygraphs", name="agencygraphs"),
    url(r"^agencies/by_country/(?P<country_name>[a-zA-Z\s]+)/(?P<language>\w+)/$", "countrygraphs", name="countrygraphs"),

    url(
        r"^countries/hss/$",
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/hss_graphs.html"}
        }, 
        name="hss_graphs"
    ),
    url(
        r"^countries/health_budget/$",
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/health_budget.html"}
        }, 
        name="health_budget_graphs"
    ),
    url(
        r"^countries/budget_disbursement/$",
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/budget_disbursement.html"}
        }, 
        name="budget_disbursement_graphs"
    ),
    url(
        r"^countries/by_indicator/(?P<indicator>\w+)/$",
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/country_graphs_by_indicator.html"}
        }, 
        name="countries_by_indicator_graphs"
    ),
)
