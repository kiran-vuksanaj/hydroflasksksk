import sqlite3
from utl.db_builder import exec, execmany

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
# USER DATABASE FUNCTIONS

def getMoney(username):
    '''def getMoney(username): get current amount of money of user in session'''
    q = "SELECT money from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    return data
