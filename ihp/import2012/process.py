import xlrd
from submissions.models import Agency, Submission, Country, DPQuestion
import os
import sys
from django.db import transaction

def unfloat(val):
    if type(val) == float:
        return str(int(val))
    return val

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

        DPQuestion.objects.filter(
            submission__country=country,
            submission__agency=agency,
            submission__type="DP"
        ).update(latest_value="", latest_year="")

        submission, _ = Submission.objects.get_or_create(
            country=country,
            agency=agency,
            type="DP"
        )

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
                    q.baseline_year=2007
                    q.baseline_value=baseline_value

                q.latest_year=2011
                q.latest_value=latest_value
                q.comments=comment
                q.save()
        return submission

if __name__ == "__main__":
    parser = SubmissionParser(sys.argv[1])
    parser.parse()
