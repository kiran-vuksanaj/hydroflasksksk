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

#====================================================
# DECK OF CARDS API FUNCTION CALLS

NEWDECK = 'https://deckofcardsapi.com/api/deck/new/shuffle/'
DRAWCARDS = 'https://deckofcardsapi.com/api/deck/{}/draw/'

def newdeck( args = {} ):
    ''' newdeck(): calls deck of cards API and creates a new deck
        RETURN VALUE: id string returned to represent deck '''
    data = http_getJSON(NEWDECK,args = args)
    if data and data['success']:
        return data['deck_id']

    print(data)
    raise RequestException("Deck of Cards newdeck: see console")

def drawcards(deck_id,n):
    ''' drawcards(): calls deck of cards API and draws n cards from the specified deck id
        RETURN VALUE: array of json-like dictionaries representing cards (see DoC docs) '''
    data = http_getJSON(
        DRAWCARDS.format(deck_id),
        args = {'count':n}
    )
    if data and data['success']:
        return data['cards']

    print(data)
    raise RequestException("Deck of Cards draw: see console")
    
