from submissions.models import GovQuestion
overrides = {
    "Benin" : {"baseline" : 4, "latest" : 3.5},
    "Burkina Faso" : {"baseline" : 4, "latest" : 4.5},
    "Burundi" : {"baseline" : 2.5, "latest" : 3},
    "DRC" : {"baseline" : 2.5, "latest" : 2.5},
    "Djibouti" : {"baseline" : 3, "latest" : 3},
    "Ethiopia" : {"baseline" : 3.5, "latest" : 3.5},
    "Mali" : {"baseline" : 4, "latest" : 3.5},
    "Mauritania" : {"baseline" : 2, "latest" : 3},
    "Mozambique" : {"baseline" : 3.5, "latest" : 4},
    "Nepal" : {"baseline" : 3.5, "latest" : 2.5},
    "Niger" : {"baseline" : 3.5, "latest" : 3.5},
    "Nigeria" : {"baseline" : 3, "latest" : 3},
    "Rwanda" : {"baseline" : 3.5, "latest" : 4},
    "El Salvador" : {"baseline" : None, "latest" : None},
    "Senegal" : {"baseline" : 3.5, "latest" : 3.5},
    "Sierra Leone" : {"baseline" : 3.5, "latest" : 3.5},
    "Sudan" : {"baseline" : 2.5, "latest" : 2},
    "Togo" : {"baseline" : 2, "latest" : 3},
    "Uganda" : {"baseline" : 4, "latest" : 3.5},
}


def override_5Ga():
    for question in GovQuestion.objects.filter(question_number="9"):
        country = question.submission.country
        values = overrides[country.country]
        question.baseline_value = values["baseline"]
        question.latest_value = values["latest"]
        question.save()
