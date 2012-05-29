import xlrd
from submissions.models import Agency, Submission, Country, DPQuestion
import os
import sys
from django.db import transaction
import json

def unfloat(val):
    if type(val) == float:
        return str(int(val))
    return val

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

class SubmissionParser(object):
    def __init__(self, f):
        self.f = f

    @transaction.commit_on_success
    def parse(self):
        # TODO - this code doesn't currently cater you years other than 2007 and 2011 
        # It also doesn't cater for currency conversion
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
        currency = v(2, 3)
        completed_by = v(0, 6)
        job = v(1, 6)

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

        baseline_year = 2007
        latest_year = 2011

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

if __name__ == "__main__":
    parser = SubmissionParser(sys.argv[1])
    parser.parse()
