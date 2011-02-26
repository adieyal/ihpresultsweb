# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from submissions.models import GovScorecardRatings, GovScorecardComments, Language, Country

class Migration(SchemaMigration):

    def forwards(self, orm):
        import pdb; pdb.set_trace()
        for ratings in orm.GovScorecardRatings.objects.all():
            for language in orm.Language.objects.all():
                # I think I need to do this in order to ensure that all objects
                # are created with the correct migration version
                c = orm.Country.objects.get(country=ratings.country.country)
                l = orm.Language.objects.get(language=language.language)
                comments, _ = orm.GovScorecardComments.objects.get_or_create(country=c, language=l)
                comments.er1 = ratings.er1
                comments.er2a = ratings.er2a
                comments.er2b = ratings.er2b
                comments.er3 = ratings.er3
                comments.er4 = ratings.er4
                comments.er5a = ratings.er5a
                comments.er5b = ratings.er5b
                comments.er6 = ratings.er6
                comments.er7 = ratings.er7
                comments.er8 = ratings.er8
                comments.save()
            
    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'GovScorecardRatings.language'
        raise RuntimeError("Cannot reverse this migration. 'GovScorecardRatings.language' and its values cannot be restored.")

    models = {
        'submissions.agency': {
            'Meta': {'object_name': 'Agency'},
            'agency': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'submissions.agencycountries': {
            'Meta': {'object_name': 'AgencyCountries'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Agency']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'submissions.agencytargets': {
            'Meta': {'object_name': 'AgencyTargets'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Agency']", 'null': 'True', 'blank': 'True'}),
            'arrow_criterion_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'arrow_criterion_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'tick_criterion_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tick_criterion_value': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'submissions.agencyworkingdraft': {
            'Meta': {'object_name': 'AgencyWorkingDraft'},
            'agency': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.Agency']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'submissions.country': {
            'Meta': {'object_name': 'Country'},
            'country': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'submissions.country8dpfix': {
            'Meta': {'unique_together': "(['agency', 'country'],)", 'object_name': 'Country8DPFix'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Agency']"}),
            'baseline_progress': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_progress': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'submissions.countryexclusion': {
            'Meta': {'unique_together': "(['country', 'question_number'],)", 'object_name': 'CountryExclusion'},
            'baseline_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question_number': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'submissions.countryscorecardoverride': {
            'Meta': {'object_name': 'CountryScorecardOverride'},
            'cd2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.Country']", 'unique': 'True'}),
            'dbr1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'dbr2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hmis1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'hmis2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hsm1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'hsm4': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'hsp1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'hsp2': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jar1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'jar4': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pf2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pfm2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pr2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rf1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'rf2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rf3': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ta2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.countrytargets': {
            'Meta': {'object_name': 'CountryTargets'},
            'arrow_criterion_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'arrow_criterion_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'tick_criterion_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tick_criterion_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.countryworkingdraft': {
            'Meta': {'object_name': 'CountryWorkingDraft'},
            'country': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.Country']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'submissions.dpquestion': {
            'Meta': {'object_name': 'DPQuestion'},
            'baseline_value': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'baseline_year': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'comments': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_value': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'latest_year': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'question_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Submission']"})
        },
        'submissions.dpscorecardratings': {
            'Meta': {'object_name': 'DPScorecardRatings'},
            'agency': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.Agency']", 'unique': 'True'}),
            'er1': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2a': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2b': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2c': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er3': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er4': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5a': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5b': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5c': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er6': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er7': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er8': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'r1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r2a': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r2b': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r2c': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r3': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r4': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r5a': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r5b': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r5c': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r6': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r7': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r8': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'submissions.dpscorecardsummary': {
            'Meta': {'object_name': 'DPScorecardSummary'},
            'agency': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.Agency']", 'unique': 'True'}),
            'erb1': ('django.db.models.fields.TextField', [], {}),
            'erb2': ('django.db.models.fields.TextField', [], {}),
            'erb3': ('django.db.models.fields.TextField', [], {}),
            'erb4': ('django.db.models.fields.TextField', [], {}),
            'erb5': ('django.db.models.fields.TextField', [], {}),
            'erb6': ('django.db.models.fields.TextField', [], {}),
            'erb7': ('django.db.models.fields.TextField', [], {}),
            'erb8': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'submissions.govquestion': {
            'Meta': {'object_name': 'GovQuestion'},
            'baseline_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'baseline_year': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'comments': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_value': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'latest_year': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'question_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Submission']"})
        },
        'submissions.govscorecardcomments': {
            'Meta': {'unique_together': "(['country', 'language'],)", 'object_name': 'GovScorecardComments'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'er1': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2a': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2b': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er3': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er4': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5a': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5b': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er6': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er7': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er8': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Language']"})
        },
        'submissions.govscorecardratings': {
            'Meta': {'unique_together': "(['country', 'language'],)", 'object_name': 'GovScorecardRatings'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'er1': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2a': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er2b': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er3': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er4': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5a': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er5b': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er6': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er7': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'er8': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Language']"}),
            'r1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r2a': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r2b': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r3': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r4': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r5a': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r5b': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r6': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r7': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'r8': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'submissions.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'submissions.mdgdata': {
            'Meta': {'object_name': 'MDGData'},
            'arrow': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'baseline_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'baseline_year': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'latest_year': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'mdg_target': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'submissions.notapplicable': {
            'Meta': {'object_name': 'NotApplicable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'variation': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'submissions.submission': {
            'Meta': {'object_name': 'Submission'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Agency']", 'null': 'True'}),
            'completed_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.Country']"}),
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'docversion': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['submissions']


