#-*- coding: utf-8 -*-
from models import Rating
from django.template import Context, Template

# agency full names
agency_name = {
    'AfDB': 'African Development Bank',
    'EC': 'European Commission',
    'GAVI': 'GAVI Alliance',
    'GFATM': 'Global Fund to fight AIDS, TB and Malaria',
    'UK': 'United Kingdom',
    'WHO': 'World Health Organisation',
    'World Bank': 'World Bank'
}

# country names - empty for now. will default to no translation.
country_name = {}

# Country Scorecard
gov_commentary_text = {
    "1G": {
        Rating.TICK : "An [space] was signed in [space] called [space].",
        Rating.ARROW : "There is evidence of a Compact or equivalent agreement under development. The aim is to have this in place by [space].",
        Rating.CROSS : "There are no current plans to develop a Compact or equivalent agreement.",
    },
    "2Ga" : {
        Rating.TICK : "A National Health Sector Plan/Strategy is in place with current targets & budgets that have been jointly assessed.",
        Rating.ARROW : "National Health Sector Plans/Strategy in place with current targets & budgets with evidence of plans for joint assessment.",
        Rating.CROSS : "National Health Sector Plans/Strategy in place with no plans for joint assessment. Target = National Health Sector Plans/Strategy in place with current targets & budgets that have been jointly assessed.",

    },
    "2Gb" : {
        Rating.TICK : "There is currently a costed and evidence based HRH plan in place that is integrated with the national health plan.",
        Rating.ARROW : """At the end of %(cur_year)s a costed and evidence based HRH plan was under development. 

At the end of %(cur_year)s a costed and evidence based HRH plan was in place but not yet integrated with the national health plan. """,
        Rating.CROSS : "At the end of %(cur_year)s there was no costed and evidence based HRH plan in place, or plans to develop one. ",
    },
    "3G" : {
        "all" : "In %(cur_year)s %(country_name)s allocated %(cur_val).1f%% of its approved annual national budget to health.",
    },
    "4G" : {
        "all" : "In %(cur_year)s, %(one_minus_cur_val).0f%% of health sector funding was disbursed against the approved annual budget.",
    },
    "5Ga" : {
        "all" : "In %(cur_year)s, %(country_name)s achieved a score of %(cur_val).1f on the PFM/CPIA scale of performance."
    },
    "5Gb" : {
        "all" : "In %(cur_year)s, %(country_name)s achieved a score of %(cur_val).0f on the four point scale used to assess performance in the the procurement sector."
    },
    "6G" : {
        Rating.TICK : "In %(cur_year)s there was a transparent and monitorable performance assessment framework in place to assess progress against (a) the national development strategies relevant to health and (b) health sector programmes.",
        Rating.ARROW : "At the end of %(cur_year)s there was evidence that a transparent and monitorable performance assessment framework was under development to assess progress against (a) the national development  strategies relevant to health and (b) health sector programmes.",
        Rating.CROSS : "At the end of %(cur_year)s there was no transparent and monitorable performance assessment framework in place and no plans to develop one were clear or being implemented.",
    },
    "7G" : {
        Rating.TICK : "Mutual assessments are being made of progress implementing commitments in the health sector, including on aid effectiveness.",
        Rating.ARROW : "Mutual assessments are being made of progress implementing commitments in the health sector, but not on aid effectiveness.",
        Rating.CROSS : "Mutual assessments are not being made of progress implementing commitments in the health sector.",
    },
    "8G" : {
        "all" : "In %(cur_year)s %(cur_val).0f%% of seats in the Health Sector Coordination Mechanism (or equivalent body) were allocated to Civil Society representatives."
    },
}

rating_question_text = "Insufficient data has been provided to enable a rating for %s."
rating_none_text = "This Standard Performance Measure was deemed not applicable to %s."

agency_rating_question_text = {
    "1DP": u"La información provista fue insuficiente para asignar una calificación a la suscripción de pactos IHP+ nacionales u otros acuerdos equivalentes por parte de la organización.",
    "2DPa": u"La información provista fue insuficiente para asignar una calificación a la asistencia para el sector salud que según informes de la organización figura en los presupuestos nacionales de salud.",
    "2DPb": u"La información provista fue insuficiente para asignar una calificación a el desarrollo de capacidades provisto por la organización a través de programas ejecutados en coordinación.",
    "2DPc": u"La información provista fue insuficiente para asignar una calificación a la asistencia para el sector salud proporcionada por la organización a través de enfoques basados en programas.",
    "3DP": u"La información provista fue insuficiente para asignar una calificación a la asistencia para el sector salud proporcionada por la organización a través de compromisos multianuales.",
    "4DP": u"La información provista fue insuficiente para asignar una calificación a los desembolsos de asistencia para el sector salud proporcionados por la organización que fueron liberados de acuerdo a un cronograma establecido.",
    "5DPa": u"La información provista fue insuficiente para asignar una calificación a la asistencia para el sector salud proporcionada por la organización en la cual se utilizaron los sistemas de adquisiciones del país.",
    "5DPb": u"La información provista fue insuficiente para asignar una calificación a la asistencia para el sector salud proporcionada por la organización en la cual se utilizaron los sistemas de gestión de las finanzas públicas del país.",
    "5DPc": u"La información provista fue insuficiente para asignar una calificación a el número de unidades de ejecución de proyectos paralelas utilizadas por la organización.",
    "6DP": u"La información provista fue insuficiente para asignar una calificación a el uso por parte de la organización de marcos nacionales de evaluación del desempeño con el fin de evaluar los avances.",
    "7DP": u"La información provista fue insuficiente para asignar una calificación a la participación de la organización en evaluaciones de avances mutuas sobre el sector salud.",
    "8DP": u"La información provista fue insuficiente para asignar una calificación a el apoyo otorgado por la organización a la participación de la sociedad civil en procesos relacionados con la política del sector salud.",
    }
agency_rating_none_text = {
    "1DP": u"La suscripción de pactos IHP+ nacionales u otros acuerdos equivalentes por parte de la organización a été jugé non applicable à %s.",
    "2DPa": u"La asistencia para el sector salud que según informes de la organización figura en los presupuestos nacionales de salud a été jugé non applicable à %s.",
    "2DPb": u"El desarrollo de capacidades provisto por la organización a través de programas ejecutados en coordinación a été jugé non applicable à %s.",
    "2DPc": u"La asistencia para el sector salud proporcionada por la organización a través de enfoques basados en programas a été jugé non applicable à %s.",
    "3DP": u"La asistencia para el sector salud proporcionada por la organización a través de compromisos multianuales a été jugé non applicable à %s.",
    "4DP": u"Los desembolsos de asistencia para el sector salud proporcionados por la organización que fueron liberados de acuerdo a un cronograma establecido a été jugé non applicable à %s.",
    "5DPa": u"La asistencia para el sector salud proporcionada por la organización en la cual se utilizaron los sistemas de adquisiciones del país a été jugé non applicable à %s.",
    "5DPb": u"La asistencia para el sector salud proporcionada por la organización en la cual se utilizaron los sistemas de gestión de las finanzas públicas del país a été jugé non applicable à %s.",
    "5DPc": u"El número de unidades de ejecución de proyectos paralelas utilizadas por la organización a été jugé non applicable à %s.",
    "6DP": u"El uso por parte de la organización de marcos nacionales de evaluación del desempeño con el fin de evaluar los avances a été jugé non applicable à %s.",
    "7DP": u"La participación de la organización en evaluaciones de avances mutuas sobre el sector salud a été jugé non applicable à %s.",
    "8DP": u"El apoyo otorgado por la organización a la participación de la sociedad civil en procesos relacionados con la política del sector salud a été jugé non applicable à %s.",
    }

gov_tb2 = "%s COUNTRY SCORECARD"
gov_pc3 = "%0.1f %% allocated to health"
gov_pc4 = "%0.1f %% increase needed to meet the Abuja target (15%%)"

agency_commentary_text = {
    "1DP" : u"Un Pacto Nacional IHP+ u otro acuerdo equivalente ha sido suscrito por la organización en el %(cur_val).0f%% de los países firmantes del Pacto IHP+ ahí donde existe. La meta establecida es del %(target_round)d%%.",
    "2DPa" : u"En el %(cur_year)s, la organización informó que el %(one_minus_cur_val).0f%% de la asistencia para el sector salud figuraba en los presupuestos nacionales del sector salud – %(one_minus_diff_direction)s frente al %(one_minus_base_val).0f%%. La meta establecida es reducir en un %(target_round)d%% la asistencia que no aparece en el presupuesto (en que ≥ 85%% debe figurar en el presupuesto).",
    "2DPb" : Template(u"En el {{ cur_year }}, el {{ cur_val|floatformat }}% del desarrollo de capacidades fue provisto por la organización a través de programas ejecutados en coordinación{% if diff_direction %} – {{ diff_direction }} frente al {{ base_val|floatformat }}%{% endif %}. La meta establecida es del {{ target_round }}%."),
    "2DPc" : u"En el %(cur_year)s, el %(cur_val).0f%% de la asistencia para el sector salud fue provisto por la organización utilizando enfoques basados en programas – %(diff_direction)s frente al %(base_val).0f%%. La meta establecida es del %(target_round)d%%.",
    "3DP" : u"En el %(cur_year)s, el %(cur_val).0f%% de la asistencia para el sector salud fue provisto por la organización en forma de compromisos multianuales – %(diff_direction)s frente al %(base_val).0f%%. La meta establecida es del %(target_round)d%%.",
    "4DP" : u"En el %(cur_year)s, el %(cur_val).0f%% de los desembolsos de la asistencia para el sector salud provista por la organización fueron liberados con base en un cronograma acordado – %(diff_direction)s frente al %(base_val).0f%% en el %(base_year)s. La meta establecida es del %(target_round)d%%.",
    "5DPa" : Template(u"En el {{ cur_year }} se utilizaron sistemas nacionales de adquisiciones para el {{ one_minus_cur_val|floatformat }}% de la asistencia para el sector salud provista por la organización{% if one_minus_diff_direction %} – {{ one_minus_diff_direction }} frente al {{ one_minus_base_val|floatformat }}%{% endif %}. La meta establecida es reducir en un {{ target_round }}% la asistencia otorgada prescindiendo de sistemas de adquisiciones (en que ≥80% debe otorgarse utilizando sistemas nacionales)."),
    "5DPb" : u"En el %(cur_year)s se utilizaron sistemas nacionales de gestión de las finanzas públicas para el %(one_minus_cur_val).0f%% de la asistencia provista por la organización – %(one_minus_diff_direction)s frente al %(one_minus_base_val).0f%%. La meta establecida es reducir en un %(target_round)d%% la asistencia otorgada prescindiendo de sistemas de gestión de las finanzas públicas (en que ≥80%% debe otorgarse utilizando sistemas nacionales).",
    "5DPc" : u"En el %(cur_year)s, el número de unidades de ejecución de proyectos (UEP) paralelas utilizadas por la organización fue de %(cur_val)s – %(diff_direction)s frente a %(base_val)s. La meta establecida es reducir en un %(target_round)d%% el número de UEP paralelas.",
    "6DP" : u"En el %(cur_year)s, la organización utilizó de manera rutinaria marcos de evaluación del desempeño con el fin de evaluar los avances en el %(cur_val).0f%% de los países firmantes del Pacto IHP+ ahí donde existe. La meta establecida es del %(target_round)d%%.",
    "7DP" : u"En el %(cur_year)s, la organización participó en evaluaciones mutuas de los avances en el sector salud en el %(cur_val).0f%% de los países firmantes del Pacto IHP+ ahí donde existe. La meta establecida es del %(target_round)d%%.",
    "8DP" : u"En el 2011, existe evidencia en el %(cur_val).0f%% de los países firmantes del Pacto IHP+ de que la organización apoyó la participación de la sociedad civil en procesos relacionados con la política del sector salud. La meta establecida es del %(target_round)d%%."
}

direction_decrease = u"una reducción" 
direction_increase = u"un incremento"
direction_nochange = u"ningún cambio" 

agency_graphs = {
    "2DPa" : {
        "title" : "2DPa: Change in %% of %(agency_name)s\\'s aid flows to the health sector <br>not reported on goverment\\'s budget",
        "yAxis" : "% change in funds not reported <br>on government\\'s budget",
    },
    "2DPa_2" : {
        "title" : "2DPa: %% of %(agency_name)s\\'s aid flows to the health sector <br>reported on goverment\\'s budget",
        "yAxis" : "% of funds reported <br>on government\\'s budget",
    },
    "2DPb" : {
        "title" : "2DPb: Change in %% of capacity development provided <br>by the %(agency_name)s through coordinated programmes",
        "yAxis" : "%% of capacity development support <br/>provided through coordinated programmes",
    },
    "2DPc" : {
        "title" : "2DPc: Change in %% of aid provided through programme based approaches",
        "yAxis" : "%% of health sector aid provided <br/>through programme based approaches",
    },
    "3DP" : {
        "title" : "3DP: % of health sector funding provided through multi-year commitments",
        "yAxis" : "%% of health sector funding provided <br>through multi-year commitments",
    },
    "4DP" : {
        "title" : "4DP: Change in %% of %s\\'s health sector aid not disbursed <br>within the year for which it was scheduled",
        "yAxis" : "%% of health sector aid disbursed <br>within the year for which it was scheduled",
    },
    "5DPa" : {
        "title" : "5DPa: % change in health sector aid to the public sector not using <br/>partner countries\\' procurement systems",
        "yAxis" : "%% change in health sector aid to the public sector <br>not using partner countries\\' procurement systems",
    },
    "5DPb" : {
        "title" : "5DPb: Change in %% of %s\\'s health sector aid to the public sector <br/>not using partner countries\\' PFM systems",
        "yAxis" : "%% change in health sector aid to the public sector<br> not using partner countries\\' PFM systems",
    },
    "5DPc" : {
        "title" : "5DPc: Change in number of %s\\'s <br/>parallel project implementation (PIUs) units",
        "yAxis" : "Number parallel <br>project implementation (PIUs) units",
    },
}

country_graphs = {
    "2DPa" : {
        "title" : "2DPa: Change in aid flows to the %(country_name)s health sector <br/>not reported on government\\'s budget",
        "yAxis" : "%% change in aid flows not reported <br/>on government\\'s budget",
    },
    "2DPa_2" : {
        "title" : "2DPa: %% of %(country_name)s\\'s aid flows to the health sector <br>reported on goverment\\'s budget",
        "yAxis" : "%% of funds reported <br>on government\\'s budget",
    },
    "2DPb" : {
        "title" : "2DPb: Change in %% of capacity development support provided to %(country_name)s <br/>health sector through coordinated programmes",
        "yAxis" : "%% of capacity development support <br/>provided through coordinated programmes",
    },
    "2DPc" : {
        "title" : "2DPc: Change in %% of health sector aid provided to %(country_name)s <br/>through programme based approaches",
        "yAxis" : "%% of health sector aid provided <br/>through programme based approaches",
    },
    "3DP" : {
        "title" : "3DP: Change in %% of health sector aid provided to %(country_name)s<br/> through multi-year commitments",
        "yAxis" : "%% of health sector funding provided <br>through multi-year commitments",
    },
    "4DP" : {
        "title" : "4DP: Change in %% of health sector aid to %(country_name)s <br/>disbursed within the year for which it was scheduled",
        "yAxis" : "%% of health sector aid disbursed <br>within the year for which it was scheduled",
    },
    "5DPa" : {
        "title" : "5DPa: %% change in health sector aid to %(country_name)s public sector <br/>not using country procurement systems.",
        "yAxis" : "%% change in health sector aid to the public sector <br>not using partner countries\\' procurement systems",
    },
    "5DPb" : {
        "title" : "5DPb: %% change in health sector aid to %(country_name)s public sector<br/> not using country PFM systems.",
        "yAxis" : "%% change in health sector aid to the public sector<br> not using partner countries\\' PFM systems",
    },
    "5DPc" : {
        "title" : "5DPc: Number of agency PIUs in place in %(country_name)s",
        "yAxis" : "Number parallel <br>project implementation (PIUs) units",
    },
}

highlevel_graphs = {
    "2DPa" : {
        "title" : "2DPa: Aggregate proportion of partner support reported on national budgets",
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "2DPb" : {
        "title" : "2DPb: Aggregate proportion of partner support for capacity-development <br/>provided through coordinated programmes in line with national strategies",
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "2DPc" : {
        "title" : "2DPc: Aggregate proportion of partner support <br/>provided as programme based approaches",
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "3DP"  : {
        "title" : "3DP: Aggregate proportion partner support <br/>provided through multi-year commitments",
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "4DP"  : {
        "title" : "4DP: % of actual health spending planned for that year",
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "5DPa" : {
        "title" : "5DPa: Aggregate partner use of country procurement systems", 
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "5DPb" : {
        "title" : "5DPb: Aggregate partner use of country public financial management systems", 
        "yAxis" : "%",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    },
    "5DPc" : {
        "title" : "5DPc: Aggregate number of parallel Project Implementation Units (PIUs)", 
        "yAxis" : "Total number of PIUs",
        "subtitle" : "* Data with baseline values from 2008 are not included",
    }
}

additional_graphs = {
    "2DPa" : {
        "series1" : "Health aid reported on budget",
        "series2" : "Health aid not on budget",
        "title" : "2DPa: Proportion of partner health aid on country budget",
    },
    "2DPb" : {
        "series1" : "Support coordinated and in line",
        "series2" : "Support not coordinated and in line",
        "title" : "2DPb: Support for capacity development that is coordinated <br/>and in line with national strategies",
    },
    "2DPc" : {
        "series1" : "% of health aid as Programme Based Approach",
        "series2" : "% of health aid not as Programme Based Approach",
        "title" : "2DPc: Support provided as Programme Based Approach",
    },
    "3DP" : {
        "series1" : "% of multi-year commitments",
        "series2" : "% not provided through multi-year commitments",
        "title" : "3DP: % of aid provided through multi-year commitments",
    },
    "4DP" : {
        "series1" : "% of aid disbursed within the year for which it was scheduled",
        "series2" : "% of aid not disbursed within the year for which it was scheduled",
        "title" : "4DP: % of health sector aid disbursed within the year for which it was scheduled",
    },
    "5DPa" : {
        "series1" : "Health aid using procurement systems",
        "series2" : "Health aid not using procurement systems",
        "title" : "5DPa: Partner use of country procurement systems",
    },
    "5DPb" : {
        "series1" : "Health aid using PFM systems",
        "series2" : "Health aid not using PFM systems",
        "title" : "5DPb: Partner use of country public financial management systems",
    },
    "5DPc" : {
        "yAxis" : "Total number of PIUs",
        "title" : "5DPc: Aggregate number of parallel Project Implementation Units (PIU)s<br/> by development partner",
    }
}

projection_graphs = {
    "2DPa" : {
        "title" : "Projected time required to meet On Budget target <br>(based on current levels of performance):2007 Baseline",
    },
    "5DPb" : {
        "title" : "Projected time required to meet PFM target <br>(based on current levels of performance):2007 Baseline",
    }
}

government_graphs = {
    "3G" : {
        "title" : "3G: Proportion of national budget allocated to health",
        "subtitle" : "* Target for Nepal is 10%",
    },
    "4G" : {
        "title" : "4G: Actual disbursement of government health budgets",
    },
    "health_workforce" : {
        "title" : "Proportion of health sector budget spent on Human Resources for Health (HRH)",
    },
    "outpatient_visits" : {
        "title" : "Number of Outpatient Department Visits per 10,000 population",
    },
    "skilled_medical" : {
        "title" : "Number of skilled medical personnel per 10,000 population",
    },
    "health_budget" : {
        "title" : "% of national budget is allocated to health (IHP+ Results data)",
    }
}

target_language = {
    "target" : "target",
    "who" : "WHO Recommended"
}

rating = "Rating"
country_data = "Country Data"
agency = "Agency"
by_agency_title = "%s Data across IHP+ Countries"
by_country_title = "Development Partners in %s"
spm = "SPM"
standard_performance_measure = "Standard Performance Measure"

spm_map = {
    #"1DP" : "Proportion of ihp+ countries in which the partner has signed commitment to (or documented support for) the ihp+ country compact, or equivalent agreement.",
    "1DP" : "Partner has signed commitment to (or documented support for) the IHP+ country compact, or equivalent agreement, where they exist.",
    "2DPa" : "Percent of aid flows to the health sector that is reported on national health sector budgets.",
    "2DPb" : "Percent of current capacity-development support provided through coordinated programmes consistent with national plans/strategies for the health sector.",
    "2DPc" : "Percent of health sector aid provided as programme based approaches.",
    "3DP" : "Percent of health sector aid provided through multi-year commitments.",
    "4DP" : "Percent of health sector aid disbursements released according to agreed schedules in annual or multi-year frameworks.",
    "5DPa" : "Percent of health sector aid that uses country procurement systems.",
    "5DPb" : "Percent of health sector aid that uses public financial management systems.",
    "5DPc" : "Number of parallel project implementation units (pius) per country.",
    #"6DP" : "Proportion of countries in which agreed, transparent and monitorable performance assessment frameworks are being used to assess progress in the health sector.",
    "6DP" : "Partner uses the single national performance assessment framework, where they exist, as the primary basis to assess progress (of support to health sector).",
    #"7DP" : "Proportion of countries where mutual assessments have been made of progress implementing commitments in the health sector, including on aid effectiveness.",
    "7DP" : "Partner has participated in mutual assessment of progress implementing commitments in the health sector, including on aid effectiveness, if a mutual assessment process exists.",
    "8DP" : "Evidence of support for civil society to be actively represented in health sector policy processes - including health sector planning, coordination & review mechanisms.",
}

gov_spm_map = {
    "1G" : "IHP+ Compact or equivalent mutual agreement in place.",
    "2Ga1" : "National Health Sector Plans/Strategy in place with current targets & budgets.",
    "2Ga2" : "National Health Sector Plans/Strategy in place with current targets & budgets that have been jointly assessed.",
    "2Gb" : "Costed and evidence-based HRH plan in place that is integrated with the national health plan.",
    "3G" : "Proportion of public funding allocated to health.",
    "4G" : "Proportion of health sector funding disbursed against the approved annual budget.",
    "5Ga" : "Public Financial Management systems for the health sector either (a) adhere to broadly accepted good practices or (b) have a reform programme in place to achieve these.",
    "5Gb" : "Country Procurement systems for the health sector either (a) adhere to broadly accepted good practices or (b) have a reform programme in place to achieve these.",
    "6G" : "An agreed transparent and monitorable performance assessment framework is being used to assess progress in the health sector.",
    "7G" : "Mutual Assessments, such as Joint Annual Health Sector Reviews, have been made of progress implementing commitments in the health sector, including on aid effectiveness.",
    "8G" : "Evidence that Civil Society is actively represented in health sector policy processes - including Health Sector planning, coordination & review mechanisms.",
}
        
indicator = "Indicator"
base_val = "base val"
cur_val = "cur val"
perc_change = "% change"

dp_table_footnote = """
<b>Important information about these ratings:</b><br/>
<em>Notes on methods:</em>
<ul>
    <li>The methodology used to undertake this exercise is available at – <a href="http://www.ihpresults.com/how/methodology/">www.ihpresults.com/how/methodology</a></li>
    <li>Standard Performance Measures (SPMs) for Country Governments and Development Partners, along with their associated targets, are available at – <a href="http://www.ihpresults.com/how/methodology/spms">www.ihpresults.com/how/methodology/spms</a></li>
    <li>The Criteria used to reach the above ratings are available at – <a href="http://www.ihpresults.net/how/methodology/rating/">www.ihpresults.net/how/methodology/rating/</a></li>
    <li>Detailed guidance on key terms and definitions is available at – <a href="http://www.ihpresults/how/data_collection">www.ihpresults/how/data_collection</a></li>
    <li>The latest available data for this exercise was from 2009. Progress may have been made in 2010 that is not reported here.</li>
    <li>Development Partner data has been aggregated to produce ratings for individual Development Partner scorecards. For more a more detailed explanation on this see – <a href="http://www.ihpresults.net/how/limitations/">www.ihpresults.net/how/limitations</a></li>
<li>SPM 5DPb: 5 countries’ data is not counted for this SPM. For more a more detailed explanation on this see – <a href="http://www.ihpresults.net/how/limitations/">www.ihpresults.net/how/limitations/</a></li>
</ul>
<br/>
<em>Notes on interpretation:</em><br/>
The exercise has been largely self-reported, and it has been difficult to find opportunities to triangulate data without imposing significant transaction costs. 
<ul>
    <li>The consistency of interpretation for key terms and definitions between participating agencies may vary within this country. This could affect the comparability of results.</li>
    <li>For Development Partner SPM ratings it is important to note that the country context has a significant impact on the extent to which progress can be made by Development Partners for each of the Standard Performance Measures. Comparisons of performance across the country offices of a single agency should be made with this in mind.
    </li>
</ul>
"""

country_table_footnote = """
<b>Important information about these ratings:</b><br/>
<em>Notes on methods:</em>
<ul>
    <li>The methodology used to undertake this exercise is available at – <a href="http://www.ihpresults.com/how/methodology/">www.ihpresults.com/how/methodology</a></li>
    <li>Standard Performance Measures (SPMs) for Country Governments and Development Partners, along with their associated targets, are available at – <a href="http://www.ihpresults.com/how/methodology/spms">www.ihpresults.com/how/methodology/spms</a></li>
    <li>The Criteria used to reach the above ratings are available at – <a href="http://www.ihpresults.net/how/methodology/rating/">www.ihpresults.net/how/methodology/rating/</a></li>
    <li>Detailed guidance on key terms and definitions is available at – <a href="http://www.ihpresults/how/data_collection">www.ihpresults/how/data_collection</a></li>
    <li>The latest available data for this exercise was from 2009. Progress may have been made in 2010 that is not reported here.</li>
    <li>Development Partner data has been aggregated to produce ratings for individual Development Partner scorecards. For more a more detailed explanation on this see – <a href="http://www.ihpresults.net/how/limitations/">www.ihpresults.net/how/limitations</a></li>
<li>SPM 5DPb: 5 countries’ data is not counted for this SPM. For more a more detailed explanation on this see – <a href="http://www.ihpresults.net/how/limitations/">www.ihpresults.net/how/limitations/</a></li>
</ul>
<br/>
<em>Notes on interpretation:</em><br/>
The exercise has been largely self-reported, and it has been difficult to find opportunities to triangulate data without imposing significant transaction costs. 
<ul>
    <li>The consistency of interpretation for key terms and definitions between participating agencies may vary within this country. This could affect the comparability of results.</li>
    </li>
</ul>
"""
