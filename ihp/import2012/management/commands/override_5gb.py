from submissions.models import GovQuestion
from submissions.consts import MISSING

overrides = {
    "Niger" : {"baseline" : "B", "latest" : "B"},
    "Rwanda" : {"baseline" : MISSING, "latest" : "B"},
    "Senegal" : {"baseline" : MISSING, "latest" : "B"},
    "Sierra Leone" : {"baseline" : MISSING, "latest" : "B"},
    "Uganda" : {"baseline" : MISSING, "latest" : "B"},
}


def override_5Gb():
    for question in GovQuestion.objects.filter(question_number="10"):
        country = question.submission.country
        values = overrides.get(country.country, MISSING)
        print values, country
        if values:
            question.baseline_value = values["baseline"]
            question.latest_value = values["latest"]
        else:
            question.baseline_value = MISSING
            question.latest_value = MISSING
        question.save()
