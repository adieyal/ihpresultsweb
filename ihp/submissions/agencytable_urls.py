from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('ihp.submissions.table_views',
    url(
        r"fragile_states/$", 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/fragile_states.html"}
        }, 
        "fragile_states"
    ),
    url(
        r'two_by_two_analysis/$', 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/two_by_two_analysis.html"}
        }, 
        "two_by_two_analysis"
    ),
    url(
        r'top5_countries/$', 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/top5_countries.html"}
        }, 
        "top5_countries"
    ),
)
