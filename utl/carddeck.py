# team hydroflask
# Softdev1 pd1
# P02 -- API calls for Deck of Cards API
# 2020-01-07

import urllib3, json

#====================================================
# URLLIB3 UTILITIES

class RequestException(Exception):
    ''' class RequestException: exception to be raised when the Deck of Cards API receives a status other than success'''
    pass

def http_getJSON( url, method = 'GET', args = {} ):
    ''' http_getJSON(): use urllib3 to issue a request to a given url and convert its response from JSON into a dictionary '''
    http = urllib3.PoolManager()
    response = http.request(method,url)
    return json.loads(response.data.decode('utf-8'))


NEWDECK = 'https://deckofcardsapi.com/api/deck/new/shuffle/'
DRAWCARDS = 'https://deckofcardsapi.com/api/deck/{}/draw/'
