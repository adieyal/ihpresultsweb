import xlrd
import datetime
from submissions.models import Agency, Submission, Country, DPQuestion, GovQuestion, CurrencyConversion
import os
import sys
from django.db import transaction
import json

def get_or_none(obj, **kwargs):
    try:
        return obj.objects.get(**kwargs)
    except obj.DoesNotExist:
        return None

def unfloat(val):
    if type(val) == float:
        return str(int(val))
    return val

def safe_mul(v1, v2):
    try:
        v1 = float(v1)
        v2 = float(v2)
    except (ValueError, TypeError):
        return None
    return v1 * v2

# countries that were added in 2012
new_countries = [
    "Benin",
    "El Salvador",
    "Mauritania",
    "Rwanda",
    "Senegal",
    "Sierra Leone",
    "Sudan",
    "Togo",
    "Uganda"
]

# question that need currency conversions
dp_conversion_questions = [
    "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
    "17", "18"
]

yes_values = ["oui", "yes", "y"]
no_values = ["non", "no", "n"]


def cellgrabber(sheet):
    def _v(r, c):
        value = sheet.cell(r, c).value
        if isinstance(value, basestring):
            return value.strip()
        return value
    return _v

class SubmissionParser(object):
    DP_SHEET = "DP"
    GOV_SHEET = "Gov"
    YES_VALUE = "yes"
    NO_VALUE = "no"

    @classmethod
    def get_parser(cls, f):
        sheet = cls.get_data_sheet(f)
        if not sheet:
            raise Exception("Could not detect file type")

        if sheet["type"] == SubmissionParser.DP_SHEET:
            return DPSubmissionParser(sheet["sheet"])
        elif sheet["type"] == SubmissionParser.GOV_SHEET:
            return GovSubmissionParser(sheet["sheet"])

    @classmethod
    def get_data_sheet(cls, fname):
        book = xlrd.open_workbook(fname)
        for sheet in book.sheets():
            if sheet.name in ["Survey Tool", "Questionnaire"]:
                if sheet.cell(7, 0).value == "1DP":
                    return {
                        "sheet" :  sheet,
                        "type" : SubmissionParser.DP_SHEET
                    }
                elif sheet.cell(6, 0).value == "1G":
                    return {
                        "sheet" :  sheet,
                        "type" : SubmissionParser.GOV_SHEET
                    }
        return None

    def __init__(self, sheet):
        self.sheet = sheet
        self.datemode = sheet.book.datemode
        self._v = cellgrabber(sheet)


    def parse_year(self, year):
        if year not in [str(y) for y in range(1990, 2020)]:
            return None
        return year

    def extract_yesno(self, row, col):
        val = self._v(row, col).lower()
        if val in yes_values:
            return SubmissionParser.YES_VALUE
        elif val in no_values:
            return SubmissionParser.NO_VALUE
        else:
            sys.stderr.write("WARNING: Unknown yes/no value: %s in row: %d, col: %d\n" % (val, row, col))
            return None

    def extract_yesno_value(self, row):
        return {
            "base_val" : self.extract_yesno(row, self.base_col),
            "cur_val" : self.extract_yesno(row, self.cur_col),
            "comments" : self.extract_comment(row),
        }

    def extract_answer(self, row):

        def s(t):
            if isinstance(t, basestring):
                if t.strip() == "": return None
                return t.strip()
            return t

        return {
            "base_val" : s(self._v(row, self.base_col)),
            "cur_val" : s(self._v(row, self.cur_col)),
            "comments" : self.extract_comment(row)
        }

    def extract_amounts(self, row, baseline_rate, cur_rate):
        answer = self.extract_answer(row)
        answer["base_val"] = safe_mul(answer["base_val"], baseline_rate)
        answer["cur_val"]  = safe_mul(answer["cur_val"], cur_rate)
        return answer

    def extract_list(self, rows, col, labels):

        lst = [
            label 
            for row, label in zip(rows, labels) 
            if self.extract_yesno(row, col) == SubmissionParser.YES_VALUE
        ]

        return lst


    def extract_comment(self, row):
        return self._v(row, self.comments_col).strip()


class DPSubmissionParser(SubmissionParser):
    def __init__(self, sheet):
        super(DPSubmissionParser, self).__init__(sheet)
        self.base_col = 5
        self.cur_col = 6
        self.comments_col = 7
        self.type = "DP"

    def extract_metadata(self):
        
        return {
            "country" : self._v(0, 3),
            "agency" : self._v(1, 3),
            "currency" : self._v(2, 3),
            "baseline_year" : self.parse_year(unfloat(self._v(3, 3))),
            "latest_year" : self.parse_year(unfloat(self._v(4, 3))),
            "completed_by" : self._v(0, 6),
            "job_title" : self._v(1, 6)
        }

    def extract_answers(self):
        q16_labels = ["financial", "technical", "lobbying", "other"]

        metadata = self.extract_metadata()
        currency = metadata["currency"]
        rate_baseline = get_or_none(CurrencyConversion, currency=currency, year=metadata["baseline_year"])
        rate_current = get_or_none(CurrencyConversion, currency=currency, year=metadata["latest_year"])

        if rate_baseline:
            rate_baseline = rate_baseline.rate

        if rate_current:
            rate_current = rate_current.rate

        return {
            "1" : self.extract_yesno_value(7),
            "2" : self.extract_amounts(8, rate_baseline, rate_current),
            "3" : self.extract_amounts(9, rate_baseline, rate_current),
            "4" : self.extract_amounts(10, rate_baseline, rate_current),
            "5" : self.extract_amounts(11, rate_baseline, rate_current),
            "6" : self.extract_amounts(12, rate_baseline, rate_current),
            "7" : self.extract_amounts(13, rate_baseline, rate_current),
            "8" : self.extract_amounts(14, rate_baseline, rate_current),
            "9" : self.extract_amounts(15, rate_baseline, rate_current),
            "10" : self.extract_amounts(16, rate_baseline, rate_current),
            "11" : self.extract_amounts(17, rate_baseline, rate_current),
            "12" : self.extract_amounts(18, rate_baseline, rate_current),
            "13" : self.extract_answer(19),
            "14" : self.extract_yesno_value(20),
            "15" : self.extract_yesno_value(21),
            "16" : {
                "base_val" : self.extract_list(range(23, 27), self.base_col, q16_labels),
                "cur_val" : self.extract_list(range(23, 27), self.cur_col, q16_labels),
                "comments" : self.extract_comment(22),
            },
            "17" : self.extract_amounts(27, rate_baseline, rate_current),
            "18" : self.extract_amounts(28, rate_baseline, rate_current),
        }

    def _4dp_switcheroo(self, submission, answers):
        answers["10old"] = answers["9"]
        answers["11old"] = answers["6"]
        if submission.country not in new_countries: 
            try:
                q10 = DPQuestion.objects.get(submission=submission, question_number="10")
                answers["10old"]["base_val"] = q10.baseline_value
                answers["10old"]["base_year"] = q10.baseline_year
            except DPQuestion.DoesNotExist:
                pass  

            try:
                q11 = DPQuestion.objects.get(submission=submission, question_number="11")
                answers["11old"]["base_val"] = q11.baseline_value
                answers["11old"]["base_year"] = q11.baseline_year
            except DPQuestion.DoesNotExist:
                pass  
            

    @transaction.commit_on_success
    def process(self):
        metadata = self.extract_metadata()
        country = Country.objects.get(country=metadata["country"])
        agency_name = metadata["agency"]
        agency = Agency.objects.all_types().get(agency=agency_name)
        submission, created = Submission.objects.get_or_create(
            country=country,
            agency=agency,
            type=Submission.DP
        )

        submission.job_title = metadata["job_title"]
        submission.completed_by = metadata["completed_by"]
        submission.save()

        answers = self.extract_answers()
        self._4dp_switcheroo(submission, answers)
        for qnum, qhash in answers.items():
            question, _ = DPQuestion.objects.get_or_create(
                submission=submission,
                question_number=qnum
            )

            if qnum == "16":
                qhash["base_val"] = json.dumps(qhash["base_val"])
                qhash["cur_val"] = json.dumps(qhash["cur_val"])

            if created or qnum in ["10old", "11old"]:
                question.baseline_value = qhash["base_val"]
                question.baseline_year = qhash["base_year"] if "base_year" in qhash else metadata["baseline_year"]
            question.latest_value = qhash["cur_val"]
            question.latest_year = metadata["latest_year"]
            question.comments = qhash["comments"]
            question.save()
        return submission

class GovSubmissionParser(SubmissionParser):
    def __init__(self, sheet):
        super(GovSubmissionParser, self).__init__(sheet)
        self.base_col = 3
        self.cur_col = 4
        self.comments_col = 5
        self.type = "Gov"

    @transaction.commit_on_success
    def process(self):

        metadata = self.extract_metadata()
        country = Country.objects.get(country=metadata["country"])
        agency_name = "Government of " + metadata["country"]
        agency = Agency.objects.all_types().get(agency=agency_name)
        submission, created = Submission.objects.get_or_create(
            country=country,
            agency=agency,
            type=Submission.Gov
        )

        for qnum, qhash in self.extract_answers().items():
            if qnum in ["15", "16"]:
                qhash["base_val"] = json.dumps(qhash["base_val"])
                qhash["cur_val"] = json.dumps(qhash["cur_val"])

            q, _ = GovQuestion.objects.get_or_create(
                submission=submission,
                question_number=qnum
            )
            
            if created:
                q.baseline_value = qhash["base_val"]
                q.baseline_year = metadata["baseline_year"]
            q.latest_value = qhash["cur_val"]
            q.latest_year = metadata["latest_year"]
            q.comments = qhash["comments"]
            q.save()
            
        return submission

    def extract_metadata(self):
        
        return {
            "country" : self._v(0, 1),
            "currency" : self._v(1, 1),
            "baseline_year" : self.parse_year(self._v(2, 1)),
            "latest_year" : self.parse_year(unfloat(self._v(3, 1))),
            "completed_by" : self._v(0, 5),
            "job_title" : self._v(1, 5)
        }

    def extract_answers(self):
        q14_labels = [
            "maternal_health", 
            "child_health", 
            "malaria", 
            "hiv_aids", 
            "tb", 
            "hss", 
            "nutrition", 
            "international_ngo", 
            "national_ngo", 
            "fbo", 
            "umbrella_organisation", 
            "pa"
        ]
        
        q15_labels = [
            "joint_reviews", 
            "monthy_meetings", 
            "working_groups", 
            "budget_development"
        ]

        

        def extract_date(row, col):
            val = self._v(row, col)
            if str(val).strip() == "": return None

            date_tuple = xlrd.xldate_as_tuple(val, self.datemode)
            return datetime.datetime(*date_tuple)

        
        def extract_date_value(row):
            return {
                "base_val" : extract_date(row, self.base_col),
                "cur_val" : extract_date(row, self.cur_col),
                "comments" : self.extract_comment(row),
            }
            
        metadata = self.extract_metadata()
        currency = metadata["currency"]
        rate_baseline = get_or_none(CurrencyConversion, currency=currency, year=metadata["baseline_year"])
        rate_current = get_or_none(CurrencyConversion, currency=currency, year=metadata["latest_year"])

        if rate_baseline:
            rate_baseline = rate_baseline.rate

        if rate_current:
            rate_current = rate_current.rate

        return {
            "1" : self.extract_yesno_value(6),
            "2" : self.extract_yesno_value(7),
            "3" : self.extract_yesno_value(8),
            "4" : self.extract_yesno_value(9),
            "5" : self.extract_amounts(10, rate_baseline, rate_current),
            "6" : self.extract_amounts(11, rate_baseline, rate_current),
            "7" : self.extract_amounts(12, rate_baseline, rate_current),
            "8" : self.extract_amounts(13, rate_baseline, rate_current),
            "9" : self.extract_answer(14),
            "10" : self.extract_answer(15),
            "11" : self.extract_yesno_value(16),
            "12" : self.extract_yesno_value(17),
            "13" : self.extract_answer(18),
            "14" : {
                "base_val" : self.extract_list(range(20, 32), self.base_col, q14_labels),
                "cur_val" : self.extract_list(range(20, 32), self.cur_col, q14_labels),
                "comments" : self.extract_comment(20),
            },
            "15" : {
                "base_val" : self.extract_list(range(33, 37), self.base_col, q15_labels),
                "cur_val" : self.extract_list(range(33, 37), self.cur_col, q15_labels),
                "comments" : self.extract_comment(32),
            },
            "16" : self.extract_answer(37),
            "17" : self.extract_answer(38),
            "18" : self.extract_answer(39),
            "19" : self.extract_answer(40),
            "20" : self.extract_answer(41),
            "21" : self.extract_amounts(42, rate_baseline, rate_current),
            "22" : self.extract_yesno_value(43),
            "23" : self.extract_answer(44),
            "24" : self.extract_answer(45),
            "25" : extract_date_value(46),
        }

