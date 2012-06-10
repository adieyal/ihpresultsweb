# -*- coding: utf8: -*-
import datetime
import os
from django.test import TestCase
from import2012.process import SubmissionParser, GovSubmissionParser, DPSubmissionParser
import submissions.models as smodels

testdir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "testfiles"
)
gov_file = os.path.join(testdir, "Niger.2012.xls")
dp_file = os.path.join(testdir, "GAVI Togo.xls")
dp_file2 = os.path.join(testdir, "UNICEF Mali.xls")

class TestGovernmentParser(TestCase):
    fixtures = ['basic.json', 'agencies.json']
    def test_parse_detect_gov_file(self):
        """
        Tests that a government file is correctly detected 
        """
        
        self.assertEquals(
            type(SubmissionParser.get_parser(gov_file)), 
            GovSubmissionParser
        )

    def test_extract_gov_metadata(self):
        parser = SubmissionParser.get_parser(gov_file)
        metadata = parser.extract_metadata()
        self.assertEquals(metadata["country"], "Niger")
        self.assertEquals(metadata["currency"], "XOF")
        self.assertEquals(metadata["baseline_year"], None)
        self.assertEquals(metadata["latest_year"], "2011")
        self.assertEquals(metadata["completed_by"], "Ousmane Oumarou")
        self.assertEquals(metadata["job_title"], "Directeur des Etudes et de la Planification")

    def test_extract_answers(self):
        parser = SubmissionParser.get_parser(gov_file)
        answers = parser.extract_answers()
        rate = 0.0021
        self.assertEquals(answers["1"]["base_val"], None)
        self.assertEquals(answers["1"]["cur_val"], "yes")
        self.assertEquals(answers["1"]["comments"], u"")

        self.assertEquals(answers["2"]["base_val"], None)
        self.assertEquals(answers["2"]["cur_val"], "yes")
        self.assertEquals(answers["2"]["comments"], u"PDS 2011-2015")

        self.assertEquals(answers["3"]["base_val"], None)
        self.assertEquals(answers["3"]["cur_val"], "yes")
        self.assertEquals(answers["3"]["comments"], u"")

        self.assertEquals(answers["4"]["base_val"], None)
        self.assertEquals(answers["4"]["cur_val"], "yes")
        self.assertEquals(answers["4"]["comments"], u"PDRH 2011-2020")

        self.assertEquals(answers["5"]["base_val"], None)
        self.assertEquals(answers["5"]["cur_val"],  734068204752.0 * rate)
        self.assertEquals(answers["5"]["comments"], u"Sources: Ministère des Finances;")

        self.assertEquals(answers["6"]["base_val"], None)
        self.assertEquals(answers["6"]["cur_val"],  40539337611.0 * rate)
        self.assertEquals(answers["6"]["comments"], u"")

        self.assertEquals(answers["7"]["base_val"], None)
        self.assertEquals(answers["7"]["cur_val"],  107318471563.0 * rate)
        self.assertEquals(answers["7"]["comments"], u"sources : budget: consolidé national des PAA 2011 et  Aide mémoire de 2012 au titre de l'année 2011")

        self.assertEquals(answers["8"]["base_val"], None)
        self.assertEquals(answers["8"]["cur_val"],  61072093186.0 * rate)
        self.assertEquals(answers["8"]["comments"], u"")

        self.assertEquals(answers["9"]["base_val"], u"Consultez fiche 'les systèmes nationaux de données'")
        self.assertEquals(answers["9"]["cur_val"],  u"Consultez fiche 'les systèmes nationaux de données'")
        self.assertEquals(answers["9"]["comments"], u"Oui, le Niger adhère aux bonnes pratiques inspirées des directives de l'UEMOA. Les procédures sont supervisées par l'ARMP (Audits, Inspoections et mécanismes de contrôle en place et fonctionnel).")

        self.assertEquals(answers["10"]["base_val"], u"Consultez fiche 'les systèmes nationaux de données'")
        self.assertEquals(answers["10"]["cur_val"],  u"Consultez fiche 'les systèmes nationaux de données'")
        self.assertEquals(answers["10"]["comments"], u"Un programme de réforme est exécuté: Le code portant code des Marchés Publics et de délégation de services publics est décidé par décret n° 2011-686/PRN du 29 déc 2011 et non par loi, ce qui facilite les modifications et autres réformes; les système de contrôle sont en place (ARMP et DGCMP)")

        self.assertEquals(answers["11"]["base_val"], None)
        self.assertEquals(answers["11"]["cur_val"],  "yes")
        self.assertEquals(answers["11"]["comments"], u"")

        self.assertEquals(answers["12"]["base_val"], None)
        self.assertEquals(answers["12"]["cur_val"],  "yes")
        self.assertEquals(answers["12"]["comments"], u"Les 12 indicateurs de performance ne sont pas systématiquement évalués")

        self.assertEquals(answers["13"]["base_val"], None)
        self.assertEquals(answers["13"]["cur_val"],  9)
        self.assertEquals(answers["13"]["comments"], u"9 altogether 7 syndicats et 2 ONG nationales these take part in the technical committee (145 members) and health committee (163 members)")

        self.assertEquals(answers["14"]["base_val"], [])
        self.assertEquals(answers["14"]["cur_val"],  ["maternal_health", "child_health", "malaria", "hiv_aids", "tb", "hss", "nutrition", "international_ngo", "national_ngo", "fbo", "pa"])
        self.assertEquals(answers["14"]["comments"], u"Le ROASN qui est un réseau des ONG intervenant dans le secteur de la santé capitalise tous les domaine d'interventions.")

        self.assertEquals(answers["15"]["base_val"], [])
        self.assertEquals(answers["15"]["cur_val"],  ["joint_reviews", "monthy_meetings", "working_groups", "budget_development"])
        self.assertEquals(answers["15"]["comments"], u"")

        self.assertEquals(answers["16"]["base_val"], None)
        self.assertEquals(answers["16"]["cur_val"],  77)
        self.assertEquals(answers["16"]["comments"], u"Source: Répertoire PTF édition 2011, complété par la Div Coopération sanitaire")

        self.assertEquals(answers["17"]["base_val"], None)
        self.assertEquals(answers["17"]["cur_val"],  5)
        self.assertEquals(answers["17"]["comments"], u"FC: 5; PAA, tous les PTF")

        self.assertEquals(answers["18"]["base_val"], None)
        self.assertEquals(answers["18"]["cur_val"],  5834)
        self.assertEquals(answers["18"]["comments"], u"Médecins, chirurgiens dentistes, pharmaciens, infirmiers, sages femmes =(489+11+389+17)+(36+22)+(261+673+474)+(67+78+1129+1506+682)")

        self.assertEquals(answers["19"]["base_val"], None)
        self.assertEquals(answers["19"]["cur_val"],  15730754)
        self.assertEquals(answers["19"]["comments"], u"")

        self.assertEquals(answers["20"]["base_val"], None)
        self.assertEquals(answers["20"]["cur_val"],  12441357)
        self.assertEquals(answers["20"]["comments"], u"Il s'agit là du total des consultations (Nouveaux contacts et visites de retour) effectuées par les Centre de santé de base, sans les hôpitaux. Les données des hôpitaux ne sont pas disponibles pour le moment. Les nouveaux contacts s'élèvent à 7 101 022")

        self.assertEquals(answers["21"]["base_val"], None)
        self.assertEquals(answers["21"]["cur_val"],  14599538492 * rate)
        self.assertEquals(answers["21"]["comments"], u"Montant voté contractuels est de 788 190 087 (MSP) + 290 035 082 (PPTE) - =13626011296+(86318731+22270616+85176632+85277640+86432536+434448+86432536+86590744+86590744+86590744+75277768+")

        self.assertEquals(answers["22"]["base_val"], None)
        self.assertEquals(answers["22"]["cur_val"],  "no")
        self.assertEquals(answers["22"]["comments"], u"Actuellement, le système d'information est en révision en vue de répondre aux préocupations de pertinence et de fiabilité")

        self.assertEquals(answers["23"]["base_val"], None)
        self.assertEquals(answers["23"]["cur_val"],  45)
        self.assertEquals(answers["23"]["comments"], u"")

        self.assertEquals(answers["24"]["base_val"], None)
        self.assertEquals(answers["24"]["cur_val"],  150)
        self.assertEquals(answers["24"]["comments"], u"")

        self.assertEquals(answers["25"]["base_val"], None)
        self.assertEquals(type(answers["25"]["cur_val"]),  datetime.datetime)
        self.assertEquals(answers["25"]["cur_val"].year,  2011)
        self.assertEquals(answers["25"]["cur_val"].month, 12)
        self.assertEquals(answers["25"]["cur_val"].day, 12)
        self.assertEquals(answers["25"]["comments"], u"12 au 16 décembre 2011 Tous les secteurs membres de chacun des 2 comités (Comité Technique National de Santé et Comité National de Santé) ont participé. Toutefois, certains partenaires techniques et financiers n'ont pas pris part aux travaux. Sur le plan redevabilité, ces revues ne donnent pas les résultats escomptés.")

    def test_load_file(self):
        self.assertEquals(smodels.Submission.objects.count(), 0)
        parser = SubmissionParser.get_parser(gov_file)
        parser.process()
        self.assertEquals(smodels.Submission.objects.count(), 1)
        submission = smodels.Submission.objects.all()[0]
        self.assertEquals(submission.govquestion_set.count(), 25)
        q = smodels.GovQuestion.objects.get(question_number=2, submission=submission)

        self.assertEquals(q.baseline_value, None)
        self.assertEquals(q.baseline_year, None)
        self.assertEquals(q.latest_value, "yes")
        self.assertEquals(q.latest_year, "2011")
        self.assertEquals(q.comments, u"PDS 2011-2015")

        q = smodels.GovQuestion.objects.get(question_number=15, submission=submission)
        self.assertEquals(q.baseline_value, "[]")
        self.assertEquals(q.latest_value, '["joint_reviews", "monthy_meetings", "working_groups", "budget_development"]')


class TestPartnerParser(TestCase):
    fixtures = ['basic.json', 'agencies.json']

    def test_parse_detect_gov_file(self):
        """
        Tests that a dp file is correctly detected 
        """
        
        self.assertEquals(
            type(SubmissionParser.get_parser(dp_file)), 
            DPSubmissionParser
        )

    def test_extract_dp_metadata(self):
        parser = SubmissionParser.get_parser(dp_file)
        metadata = parser.extract_metadata()
        self.assertEquals(metadata["country"], "Togo")
        self.assertEquals(metadata["agency"], "GAVI")
        self.assertEquals(metadata["currency"], "USD")
        self.assertEquals(metadata["baseline_year"], "2007")
        self.assertEquals(metadata["latest_year"], "2011")
        self.assertEquals(metadata["completed_by"], "Farouk Shamas Jiwa (Mato)")
        self.assertEquals(metadata["job_title"], "Programme Officer")

    def test_extract_answers(self):
        parser = SubmissionParser.get_parser(dp_file)
        answers = parser.extract_answers()
        self.assertEquals(answers["1"]["base_val"], "no")
        self.assertEquals(answers["1"]["cur_val"],  "no")
        self.assertEquals(answers["1"]["comments"], u"In all IHP+ countries the GAVI Alliance is represented by partners at country level, and does not sign country compacts.  Country-specific information for over 70 countries approved for GAVI support since its inception in 2000, including approved proposals, reports & financial plans, immunisation coverage rates and latest news can be found on the GAVI website: http://www.gavialliance.org/country/")

        self.assertEquals(answers["2"]["base_val"], 765096.46)
        self.assertEquals(answers["2"]["cur_val"],  2287729.24)
        self.assertEquals(answers["2"]["comments"], u"GAVI encourages countries to record GAVI contributions on national budgets")

        self.assertEquals(answers["3"]["base_val"], None)
        self.assertEquals(answers["3"]["cur_val"],  None)
        self.assertEquals(answers["3"]["comments"], u"")

        self.assertEquals(answers["4"]["base_val"], 0)
        self.assertEquals(answers["4"]["cur_val"],  0)
        self.assertEquals(answers["4"]["comments"], u"GAVI does not directly provide technical assistance to countries.Technical assistance  is provided by GAVI Alliance partners, including UNICEF, the World Bank, and World Health Organisation.")

        self.assertEquals(answers["5"]["base_val"], 0)
        self.assertEquals(answers["5"]["cur_val"],  0)
        self.assertEquals(answers["5"]["comments"], u"")

        self.assertEquals(answers["6"]["base_val"], 765096)
        self.assertEquals(answers["6"]["cur_val"],  2287729)
        self.assertEquals(answers["6"]["comments"], u"GAVI's support to the country for immunisation and health system activities is programme-based.")

        self.assertEquals(answers["7"]["base_val"], 765096.46)
        self.assertEquals(answers["7"]["cur_val"],  2287729.24)
        self.assertEquals(answers["7"]["comments"], u"")

        self.assertEquals(answers["8"]["base_val"], 765096.46)
        self.assertEquals(answers["8"]["cur_val"],  2042691.24)
        self.assertEquals(answers["8"]["comments"], u"GAVI supports countries for the duration of the health and immunisation plan, and is therefore multi-year by design")

        self.assertEquals(answers["9"]["base_val"], 767680)
        self.assertEquals(answers["9"]["cur_val"],  2490500)
        self.assertEquals(answers["9"]["comments"], u"Amounts not disbursed in the baseline year have been subsequently reprogrammed or written-off.")

        self.assertEquals(answers["10"]["base_val"], 14096.46)
        self.assertEquals(answers["10"]["cur_val"],  2042691.24)
        self.assertEquals(answers["10"]["comments"], u"GAVI supports the use of country systems. While countries have the option to self-procure vaccines, the vast majority choose to use the global procurment mechanism (via UNICEF) to ensure quality and value.")

        self.assertEquals(answers["11"]["base_val"], 0)
        self.assertEquals(answers["11"]["cur_val"],  0)
        self.assertEquals(answers["11"]["comments"], u"")

        self.assertEquals(answers["12"]["base_val"], None)
        self.assertEquals(answers["12"]["cur_val"],  None)
        self.assertEquals(answers["12"]["comments"], u"GAVI uses PFM systems, wherever possible, and does not use separate Project Implementation Units")

        self.assertEquals(answers["13"]["base_val"], 0)
        self.assertEquals(answers["13"]["cur_val"],  0)
        self.assertEquals(answers["13"]["comments"], u"GAVI uses PFM systems, wherever possible, and does not use separate Project Implementation Units")

        self.assertEquals(answers["14"]["base_val"], "yes")
        self.assertEquals(answers["14"]["cur_val"],  "yes")
        self.assertEquals(answers["14"]["comments"], u"GAVI assesses results through Annual Progress Reports provided by countries, which use existing national indicators, including for immunisation coverage rates.")

        self.assertEquals(answers["15"]["base_val"], None)
        self.assertEquals(answers["15"]["cur_val"],  None)
        self.assertEquals(answers["15"]["comments"], u"GAVI does not duplicate existing efforts by undertaking its own mutual assessments. GAVI also increasingly participates in the JARs (not just through partners at country level)")

        self.assertEquals(answers["16"]["base_val"], [])
        self.assertEquals(answers["16"]["cur_val"],  ['financial'])
        self.assertEquals(answers["16"]["comments"], u"For GAVI, civil society is a critical partner in immunisation service delivery, policy development, and advocacy.  Civil society, working in partnership with government in a number of GAVI eligible countries, ensures the delivery of vaccines to the children that need them the most.")

        self.assertEquals(answers["17"]["base_val"], 0)
        self.assertEquals(answers["17"]["cur_val"],  0)
        self.assertEquals(answers["17"]["comments"], u"")

        self.assertEquals(answers["18"]["base_val"], None)
        self.assertEquals(answers["18"]["cur_val"],  None)
        self.assertEquals(answers["18"]["comments"], u"")

    def test_load_file(self):
        self.assertEquals(smodels.Submission.objects.count(), 0)
        parser = SubmissionParser.get_parser(dp_file)
        parser.process()
        self.assertEquals(smodels.Submission.objects.count(), 1)
        submission = smodels.Submission.objects.all()[0]
        self.assertEquals(submission.dpquestion_set.count(), 20)
        q = smodels.DPQuestion.objects.get(question_number=2, submission=submission)

        self.assertEquals(q.baseline_value, "765096.46")
        self.assertEquals(q.baseline_year, "2007")
        self.assertEquals(q.latest_value, "2287729.24")
        self.assertEquals(q.latest_year, "2011")
        self.assertEquals(q.comments, u"GAVI encourages countries to record GAVI contributions on national budgets")

        q = smodels.DPQuestion.objects.get(question_number=16, submission=submission)
        self.assertEquals(q.baseline_value, "[]")
        self.assertEquals(q.latest_value, '["financial"]')


    def test_4dp_switcheroo_new_country(self):
        parser = SubmissionParser.get_parser(dp_file)
        parser.process()
        submission = smodels.Submission.objects.all()[0]
        q = smodels.DPQuestion.objects.get(question_number="10old", submission=submission)

        self.assertEquals(q.baseline_value, "767680.0")
        self.assertEquals(q.latest_value, "2490500.0")
        self.assertEquals(q.comments, u"Amounts not disbursed in the baseline year have been subsequently reprogrammed or written-off.")

        q = smodels.DPQuestion.objects.get(question_number="11old", submission=submission)

        self.assertEquals(q.baseline_value, "765096.0")
        self.assertEquals(q.latest_value, "2287729.0")
        self.assertEquals(q.comments, u"GAVI's support to the country for immunisation and health system activities is programme-based.")

    def test_4dp_switcheroo_old_country(self):
        agency = smodels.Agency.objects.get(agency="UNICEF")
        country = smodels.Country.objects.get(country="Mali")
        submission, _ = smodels.Submission.objects.get_or_create(
            agency=agency, country=country, type=smodels.Submission.DP
        )
        smodels.DPQuestion.objects.create(
            question_number=10, submission=submission, baseline_value="1", baseline_year=2000
        )
        smodels.DPQuestion.objects.create(
            question_number=11, submission=submission, baseline_value="2", baseline_year=2001
        )
    
        parser = SubmissionParser.get_parser(dp_file2)
        parser.process()
        self.assertEquals(smodels.Submission.objects.count(), 1)
        q = smodels.DPQuestion.objects.get(question_number="10old", submission=submission)

        self.assertEquals(q.baseline_value, "1")
        self.assertEquals(q.baseline_year, "2000")
        self.assertEquals(q.latest_value, "277828.53")
        self.assertEquals(q.comments, u"Les ressources non planifiees ont ete engagees en 2011 comme par exemple les 8 campagnes de JNV et l'étude ABCE")

        q = smodels.DPQuestion.objects.get(question_number="11old", submission=submission)

        self.assertEquals(q.baseline_value, "2")
        self.assertEquals(q.baseline_year, "2001")
        self.assertEquals(q.latest_value, "13104165.17")
        self.assertEquals(q.comments, u"Ce montant correspondant aux décaissement réels, contient des appuis pour le secteur eau-hygiène-assainissement. Il ne contient pas les coûts de staffing.")

