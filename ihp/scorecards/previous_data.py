# OK, not my proudest moment but it did not make sense to create a
# database table for 11 static values per country.

import json

data = json.load(open('olddata.json'))
empty = {
    "commitments.hrh_plan": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.health_funding": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.civilsociety": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.accountability": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.fundingcommitments": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.performance_scale": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.mutual_agreement": {
        "value": 0, 
        "year": "2009"
        }, 
    "financing.health_finance": {
        "domestic": 0, 
        "name": "2010", 
        "external": 0
        }, 
    "commitments.health_plan": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.cipa_scale": {
        "value": 0, 
        "year": "2009"
        }, 
    "commitments.resources": {
        "value": 0, 
        "year": "2009"
        }
    }
def get2010value(country, key):
    if not data.has_key(country.country):
        return empty[key]
    return data[country.country][key]
