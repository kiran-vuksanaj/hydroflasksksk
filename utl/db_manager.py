import sqlite3
from utl.db_builder import exec, execmany
from datetime import datetime
from datetime import timedelta

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

def updateTime(username):
    '''def updateTime(username): updates the time of the next daily spin of wheel of fortune'''
    q="SELECT time FROM user_tbl WHERE username=?"
    inputs=(username,)
    time=execmany(q,inputs).fetchone()[0]
    if(time==0):
        q="UPDATE user_tbl SET time=? WHERE username=?"
        now=datetime.now()+timedelta(days=1)
        now=str(now.strftime("%Y-%m-%d %H:%M:%S"))
        inputs=(now,username)
        execmany(q,inputs)
        return now
    time=time.split(" ")
    time[1]=str(time[1]).split(":")
    time[0]=str(time[0]).split("-")
    prev=datetime(int(time[0][0]),int(time[0][1]),int(time[0][2]),int(time[1][0]),int(time[1][1]),int(time[1][2]))
    now=datetime.now()
    if(now>prev):
        q="UPDATE user_tbl SET time=? WHERE username=?"
        now=datetime.now()+timedelta(days=1)
        now=str(now.strftime("%Y-%m-%d %H:%M:%S"))
        inputs=(now,username)
        execmany(q,inputs)
        return now
    else:
        return 'NONE'

def getTime(username):
    '''def updateTime(username): returns the time of the next daily spin of wheel of fortune'''
    q="SELECT time FROM user_tbl WHERE username=?"
    inputs=(username,)
    time=execmany(q,inputs).fetchone()[0]
    time=time.split(" ")
    time[1]=str(time[1]).split(":")
    time[0]=str(time[0]).split("-")
    prev=datetime(int(time[0][0]),int(time[0][1]),int(time[0][2]),int(time[1][0]),int(time[1][1]),int(time[1][2]))
    prev=str(prev.strftime("%Y-%m-%d %H:%M:%S"))
    return prev
