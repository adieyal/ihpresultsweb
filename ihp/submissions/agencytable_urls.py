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
        name="fragile_states"
    ),
    url(
        r'two_by_two_analysis/$', 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/two_by_two_analysis.html"}
        }, 
        name="two_by_two_analysis"
    ),
    url(
        r'top5_countries/$', 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/top5_countries.html"}
        }, 
        name="top5_countries"
    ),
    url(
        r'early_signatories/$', 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/early_signatories.html"}
        }, 
        name="early_signatories"
    ),
    url(
        r'volumes_by_country/$', 
        direct_to_template, 
        {
            "template" : "submissions/main_base_bootstrap.html", 
            "extra_context" : {"content_file" : "submissions/volumes_by_country.html"}
        }, 
        name="volumes_by_country"
    ),
)
