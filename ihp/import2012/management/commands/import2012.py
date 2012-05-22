import sys
import os
from collections import defaultdict, Counter
import iso8601
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from ihp.import2012.process import SubmissionParser

from submissions.models import *
import json

conversion = {
    "AUD" : {"2005" : 0.7627,  "2006" : 0.7532,  "2007" : 0.8384,  "2010" : 0.9195,  "2011" : 1.0331},
    "BIF" : {"2005" : 0.0009,  "2006" : 0.001 ,  "2007" : 0.0009,  "2010" : 0.0008,  "2011" : 0.0008},
    "CDF" : {"2005" : 0.0023,  "2006" : 0.0023,  "2007" : 0.0023,  "2010" : 0.0011,  "2011" : 0.0011},
    "DJF" : {"2005" : 0.0058,  "2006" : 0.0057,  "2007" : 0.0057,  "2010" : 0.0057,  "2011" : 0.0057},
    "ETB" : {"2005" : 0.1152,  "2006" : 0.1148,  "2007" : 0.1114,  "2010" : 0.07  ,  "2011" : 0.0589},
    "EUR" : {"2005" : 1.2456,  "2006" : 1.2557,  "2007" : 1.3702,  "2010" : 1.3279,  "2011" : 1.3926},
    "GBP" : {"2005" : 1.821 ,  "2006" : 1.8422,  "2007" : 2.0012,  "2010" : 1.546 ,  "2011" : 1.6042},
    "MRO" : {"2005" : 0.0037,  "2006" : 0.0037,  "2007" : 0.0038,  "2010" : 0.0036,  "2011" : 0.0036},
    "MZN" : {"2005" : 0.0446,  "2006" : 0.0386,  "2007" : 0.0391,  "2010" : 0.0307,  "2011" : 0.0348},
    "NGN" : {"2005" : 0.0076,  "2006" : 0.0078,  "2007" : 0.008 ,  "2010" : 0.0066,  "2011" : 0.0064},
    "NPR" : {"2005" : 0.0142,  "2006" : 0.0139,  "2007" : 0.0151,  "2010" : 0.0137,  "2011" : 0.0135},
    "RWF" : {"2005" : 0.0018,  "2006" : 0.0018,  "2007" : 0.0018,  "2010" : 0.0017,  "2011" : 0.0017},
    "SDG" : {"2005" : 0.498 ,  "2006" : 0.498 ,  "2007" : 0.498 ,  "2010" : 0.4294,  "2011" : 0.3759},
    "SEK" : {"2005" : 0.1343,  "2006" : 0.1358,  "2007" : 0.1482,  "2010" : 0.1391,  "2011" : 0.1543},
    "SLL" : {"2005" : 0.0004,  "2006" : 0.0004,  "2007" : 0.0004,  "2010" : 0.0003,  "2011" : 0.0002},
    "SVC" : {"2005" : 0.1143,  "2006" : 0.1145,  "2007" : 0.1144,  "2010" : 0.1144,  "2011" : 0.1144},
    "UGX" : {"2005" : 0.0006,  "2006" : 0.0005,  "2007" : 0.0006,  "2010" : 0.0005,  "2011" : 0.0004},
    "XOF" : {"2005" : 0.0019,  "2006" : 0.0019,  "2007" : 0.0021,  "2010" : 0.002 ,  "2011" : 0.0021},
    "USD" : {"2005" : 1.0000,  "2006" : 1.0000,  "2007" : 1.0000,  "2010" : 1.0000,  "2011" : 1.0000},
    "Cur" : {"2005" : 1.2456,  "2006" : 1.2557,  "2007" : 1.3702,  "2010" : 1.3279,  "2011" : 1.3926}, # I think this is meant to be Euro
    "NOK" : {"2005" : 0.1553,  "2006" : 0.1561,  "2007" : 0.1711,  "2010" : 0.1657,  "2011" : 0.1786},
}

dp_question_map = {
    161 : {"q" : "1", "type" : "value"},
    162 : {"q" : "1", "type" : "comment"},
    163 : {"q" : "2", "type" : "currency"},
    164 : {"q" : "3", "type" : "currency"},
    165 : {"q" : "3", "type" : "comment"},
    166 : {"q" : "4", "type" : "currency"},
    167 : {"q" : "5", "type" : "currency"},
    168 : {"q" : "5", "type" : "comment"},
    169 : {"q" : "6", "type" : "currency"},
    170 : {"q" : "7", "type" : "currency"},
    171 : {"q" : "7", "type" : "comment"},
    172 : {"q" : "8", "type" : "currency"},
    173 : {"q" : "8", "type" : "comment"},
    174 : {"q" : "9", "type" : "currency"},
    175 : {"q" : "9", "type" : "comment"},
    176 : {"q" : "10", "type" : "currency"},
    177 : {"q" : "11", "type" : "currency"},
    178 : {"q" : "11", "type" : "comment"},
    179 : {"q" : "12", "type" : "currency"},
    180 : {"q" : "12", "type" : "comment"},
    181 : {"q" : "13", "type" : "value"},
    182 : {"q" : "13", "type" : "comment"},
    183 : {"q" : "14", "type" : "value"},
    184 : {"q" : "14", "type" : "comment"},
    185 : {"q" : "15", "type" : "value"},
    186 : {"q" : "15", "type" : "comment"},
    187 : {"q" : "16", "type" : "checkbox"},
    188 : {"q" : "16", "type" : "comment"},
    189 : {"q" : "17", "type" : "currency"},
    190 : {"q" : "18", "type" : "currency"},
    191 : {"q" : "18", "type" : "comment"},
}

gov_question_map = {
    192 : {"q" : "1", "type" : "value"},
    193 : {"q" : "1", "type" : "comment"},
    194 : {"q" : "2", "type" : "value"},
    195 : {"q" : "3", "type" : "value"},
    196 : {"q" : "3", "type" : "comment"},
    197 : {"q" : "4", "type" : "value"},
    198 : {"q" : "4", "type" : "comment"},
    199 : {"q" : "5", "type" : "currency"},
    200 : {"q" : "6", "type" : "currency"},
    201 : {"q" : "6", "type" : "comment"},
    202 : {"q" : "7", "type" : "currency"},
    203 : {"q" : "8", "type" : "currency"},
    204 : {"q" : "8", "type" : "comment"},
    205 : {"q" : "9", "type" : "value"},
    206 : {"q" : "9", "type" : "comment"},
    207 : {"q" : "10", "type" : "value"},
    208 : {"q" : "10", "type" : "comment"},
    209 : {"q" : "11", "type" : "value"},
    210 : {"q" : "11", "type" : "comment"},
    211 : {"q" : "12", "type" : "value"},
    212 : {"q" : "12", "type" : "comment"},
    213 : {"q" : "13", "type" : "value"},
    214 : {"q" : "13+", "type" : "comment"},
    215 : {"q" : "14", "type" : "checkbox"},
    216 : {"q" : "14+", "type" : "comment"},
    217 : {"q" : "15", "type" : "checkbox"},
    218 : {"q" : "15+", "type" : "comment"},
    219 : {"q" : "16", "type" : "value"},
    220 : {"q" : "16+", "type" : "comment"},
    221 : {"q" : "17", "type" : "value"},
    222 : {"q" : "17+", "type" : "comment"},
    223 : {"q" : "18", "type" : "value"},
    224 : {"q" : "18+", "type" : "comment"},
    225 : {"q" : "19", "type" : "value"},
    226 : {"q" : "19+", "type" : "comment"},
    227 : {"q" : "20", "type" : "value"},
    228 : {"q" : "20+", "type" : "comment"},
    229 : {"q" : "21", "type" : "value"},
    230 : {"q" : "21+", "type" : "comment"},
    231 : {"q" : "22", "type" : "value"},
    232 : {"q" : "22+", "type" : "comment"},
    233 : {"q" : "23", "type" : "value"},
    234 : {"q" : "23+", "type" : "comment"},
    235 : {"q" : "24", "type" : "value"},
    236 : {"q" : "24+", "type" : "comment"},
    237 : {"q" : "25", "type" : "date"},
    238 : {"q" : "25+", "type" : "comment"},
    239 : {"q" : "26", "type" : "comment"},
    240 : {"q" : "27", "type" : "comment"},
}


class ResponseManager(object):
    def __init__(self, db):
        self.db = db
        self._responses = defaultdict(dict, {})

    def add(self, response):
        response_set_pk = response.response_set["pk"]

        submission = self.db["models"]["submissions"][response_set_pk]
        qnum = response.question
        
        key = submission
        old_response = self._responses[key].setdefault(qnum, response)
        if old_response.submission_date < response.submission_date:
            self._responses[key][qnum] = response

    @property
    def latest_responses(self):
        return self._responses

class ResponseSet(object):
    @staticmethod
    def from_pk(db, pk):
        return db["js"]["response_sets"][pk]

class Response(object):
    def __init__(self, db, js):
        self.js = js
        self.db = db

    @property
    def pk(self):
        return self.js["pk"]

    @property
    def response_set(self):
        response_set_pk = self.js["fields"]["response_set"]
        return ResponseSet.from_pk(self.db, self.js["fields"]["response_set"])
    
    @property
    def year(self):
        dataseries = self.response_set["fields"]["data_series"]
        years = self.db["js"]["years"]
        year_pks = [year for year in years if year in dataseries]
        if len(year_pks) != 1:
            raise Exception("Expected exactly one year dataseries")
        return years[year_pks[0]]

    @property
    def question(self):
        return self.js["fields"]["question"]

    @property
    def v1_question(self):
        return dp_question_map[self.question]["q"]

    @property
    def question_type(self):
        return dp_question_map[self.question]["type"]

    @property
    def value(self):
        value = json.loads(self.js["fields"]["value"])
        if type(value) == dict:
            v = value["value"]
        else:
            v = value

        if self.question_type == "currency" and v:
            return self._currency_value(v)
        return v

    def _currency_value(self, value):
        currency = value[0:3]
        factor = conversion[currency][self.year]
            
        return factor * float(value[3:])
        

    @property
    def submission_date(self):
        return iso8601.parse_date(self.js["fields"]["submission_date"])

class Command(BaseCommand):
    args = '<json file>'
    help = 'Import data from the 2012 system'

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.responseset_map = {}
        self.years = { # mapping between year data series and years
            32 : "2005",
            10 : "2006",
            9 : "2007",
            8 : "2008",
            5 : "2011",
        }

        self.collections = { # mapping between data collection series and baseline/current
            20 : "baseline",
            21 : "2011",
            22 : "2012",     
        }
    def get_models(self, js, model):
        return dict([(el["pk"], el) for el in js if el["model"] == model])

    @transaction.commit_on_success
    def process_agencies(self, db):
        agencies = db["js"]["agencies"]
        for pk, agency in agencies.items():
            abbr = agency["fields"]["abbreviation"]
            a, _ = Agency.objects.get_or_create(agency=abbr)
            a.display_name=agency["fields"]["name"]
            a.type="Agency"
            a.save()
            db["models"]["agencies"][pk] = a

    @transaction.commit_on_success
    def process_countries(self, db):
        countries = db["js"]["countries"]

        for pk, country in countries.items():
            c, _ = Country.objects.get_or_create(
                country=country["fields"]["name"],
                description="",
            )
            db["models"]["countries"][pk] = c

        govts = db["js"]["governments"]
        for pk, govt in govts.items():
            abbr = govt["fields"]["name"]
            a, _ = Agency.objects.get_by_type("Government").get_or_create(agency=abbr)
            a.display_name = govt["fields"]["name"]
            a.type="Government"
            a.save()
            db["models"]["agencies"][pk] = a

    @transaction.commit_on_success
    def process_responsesets2012(self, db):
        response_sets = db["js"]["response_sets_2012"]
        for response_sets in [db["js"]["response_sets_2012"], db["js"]["response_sets_baseline"]]:
            for pk, rs in response_sets.items():
                dataseries = rs["fields"]["data_series"]
                agency = db["models"]["agencies"][rs["fields"]["entity"]]
                country = [
                    db["models"]["countries"][cpk] 
                    for cpk in dataseries 
                    if cpk in db["models"]["countries"]
                ][0]

                survey_type = {3 : "DP", 4 : "Gov"}[rs["fields"]["survey"]]
                s, created = Submission.objects.get_or_create(
                    country=country,
                    agency=agency,
                    type=survey_type
                )
                s.docversion = "XXX"
                s.date_submitted = iso8601.parse_date(rs["fields"]["submission_date"])
                #s.collection = collection2012 # TODO don't forget about resolving this
                s.save()

                db["models"]["submissions"][pk] = s


    def prepare_dp_questions(self):
        # Remove all the latest year values
        DPQuestion.objects.all().update(
            latest_year="",
            latest_value=""
        )

        # Since question numbers changed between the 2010 and 2012 surveys
        # and since baseline is retained, there is a need to move these values around into the correct question numbers

        # map baseline answers from old question numbers to new
        # order matters take care to ensure that
        # a question appears on the left before
        # it appears on the right

        mapping = [
            ("14", "2"),
            ("17", "14"),
            ("8", "6"),
            ("9", "8"),
            ("10", "10old"),
            ("12", "10"),
            ("15", "12"),
            ("18", "15"),
            ("11", "11old"),
            ("13", "11"),
            ("16", "13"),
            ("20", "16"),
        ]

        for submission in Submission.objects.filter(type="DP"):
            questions = submission.dpquestion_set.all()
            for (fq, tq) in mapping:
                try:
                    questions.filter(question_number=tq).delete()
                    from_question = questions.get(question_number=fq)
                    from_question.question_number=tq
                    from_question.save()
                except DPQuestion.DoesNotExist:
                    print "Question %s does not question for %s" % (fq, submission)

    def additional_imports(self):
        from django.conf import settings
        from glob import glob
        import_dir = os.path.join(settings.PROJECT_HOME, "dropbox") 
        if not os.path.exists(import_dir):
            sys.stderr.write("No drop folder found at %s" % import_dir)
            return

        for f in glob("%s/*.xls" % import_dir):
            parser = SubmissionParser(f)
            parser.parse()

    @transaction.commit_on_success
    def process_responses(self, db):
        self.prepare_dp_questions()

        # Process the 2012 responses first
        responses2012 = db["js"]["responses_2012"]
        
        dp_submissions = db["js"]["response_sets_dp"]

        dp_responses = dict([
            (pk, rs) 
            for pk, rs in responses2012.items() 
            if rs.response_set["pk"] in dp_submissions
        ])
            
        rm = ResponseManager(db)

        for pk, response in dp_responses.items():
            rm.add(response) 

        for submission, responses in rm.latest_responses.items():

            for response in responses.values():
                v1_qn = response.v1_question
                v1_qtype = response.question_type

                dpq, created = DPQuestion.objects.get_or_create(
                    submission=submission,
                    question_number=v1_qn
                )

                dpq.latest_year = response.year
                if v1_qtype == "comment":
                    dpq.comments = response.value
                else:
                    dpq.latest_value = response.value if response.value != None else ""
                dpq.save()

                # This is really ugly - but it's better to keep the ugliness
                # in the import logic. In the 2012 survey - 4DP is a different
                # indicator to the 2010 survey. In short, Q9 in 2012 doesn't
                # map to anything in 2010. In order to accurately calculate 
                # DP in both the baseline and latest year, we copy across values
                # in both surveys to a new question
                # for the baseline the mapping is 10 => 10old and 11 => 11old
                # in the 2012 survey the mapping is 6 => 11old and 9 => 10old
                mapping = {"6" : "11old", "9" : "10old"}
                if v1_qn in mapping:
                    new_q = mapping[v1_qn]
                    dpq2, created = DPQuestion.objects.get_or_create(
                        submission=submission,
                        question_number=new_q
                    )
                    dpq2.comment = dpq.comments
                    dpq2.latest_value = dpq.latest_value
                    dpq2.latest_year = dpq.latest_year
                    dpq2.save()
        
        # Now process baseline values
        responses_baseline = db["js"]["responses_baseline"]
        dp_responses = dict([
            (pk, rs) 
            for pk, rs in responses_baseline.items() 
            if rs.response_set["pk"] in dp_submissions
        ])

        rm = ResponseManager(db)

        for pk, response in dp_responses.items():
            rm.add(response) 

        for submission, responses in rm.latest_responses.items():
            for response in responses.values():
                v1_qn = response.v1_question
                v1_qtype = response.question_type
                key = (submission.agency, submission.country)

                try:
                    dpq = DPQuestion.objects.get(
                        submission=submission,
                        question_number=v1_qn
                    )

                    dpq.baseline_year = response.year
                    if v1_qtype == "comment":
                        pass
                    else:
                        if not dpq.baseline_value:
                            dpq.baseline_value = response.value if response.value != None else ""
                    dpq.save()
                except DPQuestion.DoesNotExist:
                    print "Could not find submission for response: %s" % response.pk
        self.additional_imports()


        
    def read_database(self, js):
        db = {}
        dp_survey = 3
        gov_survey = 4
        surveys2012 = [dp_survey, gov_survey]
        collection2012 = 22
        collection_baseline = 20

        entities = self.get_models(js, "scorecard_processor.entity")
        agencies = dict([(pk, a) for pk, a in entities.items() if a["fields"]["entity_type"] == "agency"])
        govts = dict([(pk, a) for pk, a in entities.items() if a["fields"]["entity_type"] == "government"])
        dataseries = self.get_models(js, "scorecard_processor.dataseries")
        countries = dict([(pk, el) for pk, el in dataseries.items() if el["fields"]["group"] == "Country"])
        years = dict([(pk, el["fields"]["name"]) for pk, el in dataseries.items() if el["fields"]["group"] == "Year"])

        response_sets = self.get_models(js, "scorecard_processor.responseset")

        def response_sets_by_collection(collection):
            return dict([
                (pk, rs)
                for pk, rs in response_sets.items() 
                if rs["fields"]["survey"] in surveys2012 and collection in rs["fields"]["data_series"]
            ])

        def responses_by_response_set(response_set):
            return dict([
                (pk, Response(db, rs)) 
                for pk, rs in responses.items() 
                if rs["fields"]["response_set"] in response_set]
            )

        response_sets_2012 = response_sets_by_collection(collection2012)
        response_sets_baseline = response_sets_by_collection(collection_baseline)

        response_sets_dp = dict([
            (pk, rs)
            for pk, rs in response_sets.items() 
            if rs["fields"]["survey"] == dp_survey
        ])

        response_sets_gov = dict([
            (pk, rs)
            for pk, rs in response_sets.items() 
            if rs["fields"]["survey"] == gov_survey
        ])

        responses = self.get_models(js, "scorecard_processor.response")

        # Only responses in 2012 response sets
        responses_2012 = responses_by_response_set(response_sets_2012)
        responses_baseline = responses_by_response_set(response_sets_baseline)
        
        db["js"] = {
            "entities" : entities,
            "agencies" : agencies,
            "governments" : govts,
            "countries" : countries,
            "response_sets" : response_sets,
            "response_sets_2012" : response_sets_2012,
            "response_sets_baseline" : response_sets_baseline,
            "response_sets_dp" : response_sets_dp,
            "response_sets_gov" : response_sets_gov,
            "responses" : responses,
            "responses_2012" : responses_2012,
            "responses_baseline" : responses_baseline,
            "years" : years,
        }

        db["models"] = defaultdict(dict, {})
        return db
        
    def handle(self, *args, **options):
        fn_json = args[0]
        js = json.load(open(fn_json))
        db = self.read_database(js)

        self.process_agencies(db)
        self.process_countries(db)
        self.process_responsesets2012(db)
        self.process_responses(db)
