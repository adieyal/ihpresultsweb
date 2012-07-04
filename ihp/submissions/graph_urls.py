from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('ihp.submissions.graphs',
    url(r"^agencies/highlevel/(?P<language>\w+)/$", "highlevelgraphs", name="highlevelgraphs"),
    url(r"^agencies/projection/(?P<language>\w+)/$", "projectiongraphs", name="projectiongraphs"),
    url(r"^agencies/(?P<indicator>\w+)/(?P<language>\w+)/$", "agency_graphs_by_indicator", name="agency_graphs_by_indicator"),
    url(r"^agencies/(?P<agency_name>[a-zA-Z\s]+)/(?P<language>\w+)/$", "agencygraphs", name="agencygraphs"),
    url(r"^agencies/by_country/(?P<country_name>[a-zA-Z\s]+)/graphs/(?P<language>\w+)/$", "countrygraphs", name="countrygraphs"),

    url(r"^countries/(?P<language>\w+)/$", "government_graphs", {
        "template_name" : "submissions/main_base.html",
        "extra_context" : {
            "content_file" : "submissions/country_graphs_by_indicator.html"
        }
    }, "government_graphs"),
)
