import xlrd
import datetime
from submissions.models import Agency, Submission, Country, DPQuestion
import os
import sys
from django.db import transaction
import json
from consts import conversion

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

    def extract_metadata(self):
        
        return {
            "country" : self._v(0, 3),
            "agency" : self._v(1, 3),
            "currency" : self._v(2, 3),
            "baseline_year" : unfloat(self._v(3, 3)),
            "latest_year" : unfloat(self._v(4, 3)),
            "completed_by" : self._v(0, 6),
            "job_title" : self._v(1, 6)
        }

    def extract_answers(self):
        q16_labels = ["financial", "technical", "lobbying", "other"]

        metadata = self.extract_metadata()
        currency = metadata["currency"]
        rate_baseline = conversion[currency].get(metadata["baseline_year"], None)
        rate_current = conversion[currency].get(metadata["latest_year"], None)

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

    @transaction.commit_on_success
    def parse(self):
        print "Processing Book: %s" % self.f
        book = xlrd.open_workbook(self.f)
        for sheet in book.sheets():
            if sheet.name == "Survey Tool":
                if sheet.cell(7, 0).value == "1DP":
                    return self.parse_dp(sheet)
                elif sheet.cell(4, 0).value == "1G":
                    parse_gov(sheet)
        else:
            print >> sys.stderr, "Unknown sheet: %s" % sheet.name

    def parse_dp(self, sheet):
        v = lambda r, c : sheet.cell(r, c).value

        country = v(0, 3)
        agency = v(1, 3)
        currency = v(2, 3).strip()
        completed_by = v(0, 6)
        job = v(1, 6)

        try:
            baseline_year = str(int(v(3, 3)))
        except ValueError:
            baseline_year = None

        try:
            latest_year = str(int(v(4, 3)))
        except ValueError:
            latest_year = None

        base_factor = conversion[currency].get(baseline_year, None)
        latest_factor = conversion[currency].get(latest_year, None)

        agency = Agency.objects.all_types().get(agency=agency)
        country = Country.objects.get(country=country)


        if country.country in new_countries:
            DPQuestion.objects.filter(
                submission__country=country,
                submission__agency=agency,
                submission__type="DP",
            ).delete()
            Submission.objects.filter(
                country=country,
                agency=agency,
                type="DP"
            ).delete()

        submission, _ = Submission.objects.get_or_create(
            country=country,
            agency=agency,
            type="DP"
        )
        DPQuestion.objects.filter(submission=submission).update(latest_value="", latest_year="")


        submission.completed_by = completed_by
        submission.job_title = job
        submission.save()


        i8dp_map = {
            23 : "financial",
            24 : "technical",
            25 : "lobbying",
            26 : "other",
        }
        i8dp_values = {
            "baseline" : [],
            "latest" : [],
        }
        for row in range(7, sheet.nrows):
            question_number = unfloat(v(row, 3))
            baseline_value = v(row, 5)
            latest_value = v(row, 6)
            if question_number in dp_conversion_questions:
                baseline_value = safe_mul(baseline_value, base_factor)
                latest_value = safe_mul(latest_value, latest_factor)

            comment = v(row, 7)

            yes_values = ["y", "yes"]
            if row in i8dp_map.keys():
                if baseline_value.lower() in yes_values:
                    i8dp_values["baseline"].append(i8dp_map[row])
                if latest_value.lower() in yes_values:
                    i8dp_values["latest"].append(i8dp_map[row])
            else:
                q, _ = DPQuestion.objects.get_or_create(
                   submission=submission,
                   question_number=question_number
                )

                if not q.baseline_value:
                    q.baseline_year=baseline_year
                    q.baseline_value=baseline_value

                q.latest_year=latest_year
                q.latest_value=latest_value
                q.comments=comment
                q.save()
        
        ###########################################################
        # Process 8DP
        q, _ = DPQuestion.objects.get_or_create(
           submission=submission,
           question_number=16
        )

        # No need to capture the baseline values for 8DP
        # because they are different to last year
        #if not q.baseline_value:
        #    q.baseline_year=baseline_year
        #    q.baseline_value=baseline_value

        q18_comments = v(22, 7)
        q.latest_year=latest_year
        q.latest_value=json.dumps(i8dp_values["latest"])
        q.comments = q18_comments
        q.save()
        ###########################################################

        ###########################################################
        # Now update the 4DP questions
        my_questions = DPQuestion.objects.filter(submission=submission)
        my_questions.filter(question_number__in=["10old", "11old"]).delete()
        if country.country in new_countries:
            q6 = my_questions.get(question_number="6")
            q9 = my_questions.get(question_number="9")
            q6.question_number = "11old"
            q6.pk = None
            q6.save()

            q9.question_number = "10old"
            q9.pk = None
            q9.save()
        else:
            q11old = DPQuestion.objects.create(submission=submission, question_number="11old")
            q10old = DPQuestion.objects.create(submission=submission, question_number="10old")
            
            q6 = my_questions.get(question_number="6")
            q9 = my_questions.get(question_number="9")
            q10 = my_questions.get(question_number="10")
            q11 = my_questions.get(question_number="11")

            q11old.baseline_value = q11.baseline_value
            q11old.baseline_year = q11.baseline_year
            q11old.latest_value = q6.latest_value
            q11old.latest_year = q6.latest_year

            q10old.baseline_value = q10.baseline_value
            q10old.baseline_year = q10.baseline_year
            q10old.latest_value = q9.latest_value
            q10old.latest_year = q9.latest_year

        ###########################################################

        
        return submission

class GovSubmissionParser(SubmissionParser):
    def __init__(self, sheet):
        super(GovSubmissionParser, self).__init__(sheet)
        self.base_col = 3
        self.cur_col = 4
        self.comments_col = 5


    def extract_metadata(self):
        
        return {
            "country" : self._v(0, 1),
            "currency" : self._v(1, 1),
            "baseline_year" : unfloat(self._v(2, 1)),
            "latest_year" : unfloat(self._v(3, 1)),
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
        rate_baseline = conversion[currency].get(metadata["baseline_year"], None)
        rate_current = conversion[currency].get(metadata["latest_year"], None)

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

if __name__ == "__main__":
    parser = SubmissionParser(sys.argv[1])
    parser.parse()
