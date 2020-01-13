import sqlite3
from utl.db_builder import exec, execmany
import sys
import random

limit = sys.maxsize
#====================================================
# SIGN UP AND LOGIN FUNCTIONS

def userValid(username,password):
    '''def userValid(username,password): determines if username is in database and password corresponds to username'''
    q = "SELECT username FROM user_tbl;"
    data = exec(q)
    for uName in data:
        if uName[0] == username:
            q = "SELECT password from user_tbl WHERE username=?"
            inputs = (username,)
            data = execmany(q, inputs)
            for passW in data:
                if (passW[0] == password):
                    return True
    return False

def addUser(username, password):
    '''def addUser(username, password): adding user from sign up, taking in form inputs and writing to data table'''
    q = "SELECT * FROM user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()
    if (data is None):
        q = "INSERT INTO user_tbl VALUES(?, ?, '', 100000, 0, '')"
        inputs = (username, password)
        execmany(q, inputs)
        return True
    return False #if username already exists

def changePass(username, password):
    '''def changePass(username, password): updating data table of user in session with new password'''
    q = "UPDATE user_tbl SET password=? WHERE username=?"
    inputs = (password, username)
    execmany(q, inputs)

#====================================================
# USER MONEY DATABASE FUNCTIONS

def getMoney(username):
    '''def getMoney(username): get current amount of money of user in session'''
    q = "SELECT money from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    return data

def checkBet(username, bet):
    '''def checkBet(username, bet): check if user is betting a valid amount'''
    money = getMoney(username)
    bet = int(bet)
    return money >= bet

def updateMoney(username, amount):
    '''def updateMoney(username, amount): updating data table of user in session with new amount'''
    q = "UPDATE user_tbl SET money=? WHERE username=?"
    money = getMoney(username)
    amount += money
    inputs = (amount, username)
    execmany(q, inputs)

#====================================================
# LOTTERY TABLE FUNCTIONS


def checkPrice(username, type):
    '''def checkPrice(username, type): check if user can afford lottery ticket'''
    money = getMoney(username)
    price = 0
    if type == "A": #dummy values
        price = 1000
    if type == "B":
        price = 10000
    return money >= price

def generateNum():
    num = []
    while len(num)<13:
        rand = random.randint(0, 9)
        num.append(rand)
    return num

def purchaseTicket(username, num, type):
    '''def purchaseTicket(username, type): purchase ticket of given type under given username'''
    if checkPrice(username, type): #if user can afford ticket
        #add to table
        id = random.randrange(limit)
        q = "SELECT id FROM lottery_tbl WHERE id=?"
        inputs = (id, )
        data = execmany(q, inputs).fetchone()
        while data is not None:
            id = random.randrange(limit)
            data = execmany(q, inputs).fetchone()
        q = "INSERT INTO lottery_tbl VALUES(?, ?, ?, ?)"
        id = type + str(id)
        strnum = ""
        for i in range(len(num)):
            if i == 11: #last number
                strnum += str(num[i])
            else:
                strnum += str(num[i]) + ","
        inputs = (id, username, strnum, 0)
        execmany(q, inputs)

        #update user table money
        if type == "A": #dummy values
            price = -1000
        if type == "B":
            price = -10000
        updateMoney(username, price)
        return True
    return False
