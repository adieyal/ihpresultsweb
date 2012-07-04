from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('ihp.submissions.views',
    # Export views
    (
        r'^agency/questionnaires/$', 
        'dp_questionnaire', 
        {}, 
        'agency_questionnaire'
    ),

    (
        r'^agency/questionnaires/2009/$', 
        'dp_questionnaire', 
        {
            "use_2009" : True
        }, 'agency_questionnaire_2009'
    ),

    (
        r'^agency/questionnaires/cols/$', 
        'dp_questionnaire', 
        {
            "template_name" : "submissions/dp_questionnaire_cols.html"
        }, 
        'agency_questionnaire_cols'
    ),

    (
        r'^agency/questionnaires/2009/cols/$', 
        'dp_questionnaire', 
        {
            "template_name" : "submissions/dp_questionnaire_cols.html",
            "use_2009" : True
        }, 
        'agency_questionnaire_cols_2009'
    ),

    (
        r'^country/questionnaires/$', 
        'gov_questionnaire', 
        {}, 
        'gov_questionnaire'
    ),

    (
        r'^country/questionnaires/2009/$', 
        'gov_questionnaire', 
        {
            "use_2009" : True
        }, 
        'gov_questionnaire_2009'
    ),
)
