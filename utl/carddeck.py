# team hydroflask
# Softdev1 pd1
# P02 -- API calls for Deck of Cards API
# 2020-01-07

import urllib3, json

NEWDECK = 'https://deckofcardsapi.com/api/deck/new/shuffle/'
DRAWCARDS = 'https://deckofcardsapi.com/api/deck/{}/draw/'

class RequestException(Exception):
    ''' class RequestException: exception to be raised when the Deck of Cards API receives a status other than success'''
    pass




