# OK, not my proudest moment but it did not make sense to create a
# database table for 11 static values per country.

from django.conf import settings
import json
import os

path_to_json = os.path.join(settings.PROJECT_HOME, "olddata.json")
data = json.load(open(path_to_json))
empty = {
    "commitments.hrh_plan": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.health_funding": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.civilsociety": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.accountability": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.fundingcommitments": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.performance_scale": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.mutual_agreement": {
        "value": 0, 
        "year": ""
        }, 
    "financing.health_finance": {
        "domestic": 0, 
        "name": "", 
        "external": 0
        }, 
    "commitments.health_plan": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.cipa_scale": {
        "value": 0, 
        "year": ""
        }, 
    "commitments.resources": {
        "value": 0, 
        "year": ""
        }
    }
def get2010value(country, key):
    if not data.has_key(country.country):
        return empty[key]
    return data[country.country][key]
    
