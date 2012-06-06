# -*- coding: utf8: -*-
import datetime
import os
from django.test import TestCase
from import2012.process import SubmissionParser, GovSubmissionParser

class TestGovernmentParser(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestGovernmentParser, self).__init__(*args, **kwargs)
        self.testdir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "testfiles"
        )

        self.gov_file = os.path.join(self.testdir, "Niger.2012.xls")
        self.dp_file = os.path.join(self.testdir, "UNAIDS Mali.xls")

    def test_parse_detect_gov_file(self):
        """
        Tests that a government file is correctly detected 
        """
        
        #self.assertFalse(SubmissionParser(self.dp_file).is_gov_sheet())
        self.assertEquals(
            type(SubmissionParser.get_parser(self.gov_file)), 
            GovSubmissionParser
        )
        #self.assertTrue(SubmissionParser(self.gov_file).is_gov_sheet())

    def test_extract_gov_metadata(self):
        parser = SubmissionParser.get_parser(self.gov_file)
        metadata = parser.extract_metadata()
        self.assertEquals(metadata["country"], "Niger")
        self.assertEquals(metadata["currency"], "XOF")
        self.assertEquals(metadata["baseline_year"], u"Données de base (NB: Compléter seulement si votre pays n'a pas participé au 2012 processus de suivi  d'IHP+Results)")
        self.assertEquals(metadata["latest_year"], "2011")
        self.assertEquals(metadata["completed_by"], "Ousmane Oumarou")
        self.assertEquals(metadata["job_title"], "Directeur des Etudes et de la Planification")

    def test_extract_answers(self):
        parser = SubmissionParser.get_parser(self.gov_file)
        answers = parser.extract_answers()
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
        self.assertEquals(answers["5"]["cur_val"],  734068204752.0)
        self.assertEquals(answers["5"]["comments"], u"Sources: Ministère des Finances;")

        self.assertEquals(answers["6"]["base_val"], None)
        self.assertEquals(answers["6"]["cur_val"],  40539337611.0)
        self.assertEquals(answers["6"]["comments"], u"")

        self.assertEquals(answers["7"]["base_val"], None)
        self.assertEquals(answers["7"]["cur_val"],  107318471563.0)
        self.assertEquals(answers["7"]["comments"], u"sources : budget: consolidé national des PAA 2011 et  Aide mémoire de 2012 au titre de l'année 2011")

        self.assertEquals(answers["8"]["base_val"], None)
        self.assertEquals(answers["8"]["cur_val"],  61072093186.0)
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
        self.assertEquals(answers["21"]["cur_val"],  14599538492)
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
