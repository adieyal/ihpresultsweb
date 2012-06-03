from submissions.models import DPQuestion
overrides = {
    ("Germany", "Rwanda") : ['financial', 'other'],
}


def override_8DP():
    for (agency, country), value in overrides.items():
        q, _ = DPQuestion.objects.get_or_create(
            submission__agency__agency=agency,
            submission__country__country=country,
            question_number=16
        )
        q.baseline_value = q.latest_value = value
        q.save()
