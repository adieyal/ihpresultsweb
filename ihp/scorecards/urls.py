from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ihp.scorecards.views',
    url(
        r'^dp/(?P<agency_id>\d+)/(?P<language>\w+)/json$', # DP Scorecard json
        'dp_scorecard_json',
        name='dp_scorecard_json'
    ),
    url(
        r'^dp/(?P<agency_id>\d+)/(?P<language>\w+)/$', # DP Scorecard svg
        'dp_scorecard',
        name='dp_scorecard'
    ),
)
