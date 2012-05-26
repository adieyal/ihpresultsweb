from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('ihp.scorecards.views',
    url(r'^dp/json/(?P<agency_id>\d+)/(?P<language>\w+)$',
        'export_dp_agency_scorecard',
        {}, name='export_dp_agency_scorecard'),
)
