from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ihp.submissions.json_views',
    url(
        r"^agencies/fragile_states/$", 
        "fragile_states", 
        name="json_fragile_states"
    ),
    url(
        r'^agencies/two_by_two_analysis/$', 
        'two_by_two_analysis', 
        name='json_two_by_two_analysis'
    ),
    url(
        r'^agencies/top5_countries/$', 
        'top5_countries', 
        name='json_top5_countries'
    ),
)
