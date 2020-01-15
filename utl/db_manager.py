import sqlite3
from utl.db_builder import exec, execmany
import sys
import random
from datetime import datetime
from datetime import timedelta

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
        q = "INSERT INTO user_tbl VALUES(?, ?, '', 50000, 0, '')"
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
<<<<<<< HEAD
# LOTTERY TABLE FUNCTIONS

def getType(id):
    '''def getType(id): get type of a lottery ticket based on its id'''
    if "A" in id:
        return "A"
    elif "B" in id:
        return "B"
    return "C"

def checkPrice(username, type):
    '''def checkPrice(username, type): check if user can afford lottery ticket'''
    money = getMoney(username)
    price = 0
    if type == "A":
        price = 2000
    if type == "B":
        price = 10000
    else:
        price = 1000
    return money >= price

def generateNum():
    '''def generateNum(): generate random numbers for lottery ticket'''
    num = []
    while len(num)<12:
        rand = random.randint(0, 9)
        num.append(rand)
    return num

def calculatePrize(type, num):
    '''def calculatePrize(id): calculate winnings for given lottery ticket numbers'''
    winnings = 0
    if type == "A":
        for i in range(4):
            if(num[i*3]<num[i*3+1] and num[i*3+1]<num[i*3+2]):
                winnings = 10000
    elif type == "B":
        for i in range(4):
            if(num[i*3]==num[i*3+1] and num[i*3+1]==num[i*3+2]):
                winnings = 100000
    else: #type C
        for i in range(4):
            if ((num[i*3] + num [i*3+1] + num[i*3+2]) % 7 == 0):
                winnings = 2500
    return winnings

def purchaseTicket(username, type):
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
        q = "INSERT INTO lottery_tbl VALUES(?, ?, ?, ?, ?)"
        id = type + str(id)
        num = generateNum()
        strnum = ""
        for i in range(len(num)):
            if i == 11: #last number
                strnum += str(num[i])
            else:
                strnum += str(num[i]) + ","
        winnings = calculatePrize(type, num)
        inputs = (id, username, strnum, winnings, 0)
        execmany(q, inputs)

        #update user table money
        if type == "A": #dummy values
            price = -2000
        elif type == "B":
            price = -10000
        else:
            price = -1000
        updateMoney(username, price)
        return id
    return -1

def checkId(id):
    '''def checkId(id): check if lottery id exists'''
    q = "SELECT * FROM lottery_tbl WHERE id=?"
    inputs = (id, )
    data = execmany(q, inputs).fetchone()
    if data is None:
        return False
    return True

def getNum(id):
    '''def getNum(id): get the lottery numbers of a ticket based on id'''
    q = "SELECT numbers FROM lottery_tbl WHERE id=?"
    inputs = (id, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    num = []
    for entry in data:
        num.append(int(entry))
    return num

def getClaimed(id):
    '''def getClaimed(id): check if ticket has been claimed already'''
    q = "SELECT claimed FROM lottery_tbl WHERE id=?"
    inputs = (id, )
    data = execmany(q, inputs).fetchone()[0]
    return data

def claimPrize(username, id):
    '''def claimPrize(username, id): allow given user to claim given lottery ticket'''
    q = "SELECT owner FROM lottery_tbl WHERE id=?"
    inputs = (id, )
    owner = execmany(q, inputs).fetchone()[0]
    if owner != username: #user doesn't own ticket
        return -1
    q = "SELECT winnings FROM lottery_tbl WHERE id=?"
    winnings = execmany(q, inputs).fetchone()[0]
    updateMoney(username, winnings) #update user's money
    q = "UPDATE lottery_tbl SET claimed=1 WHERE id=?" #mark ticket as claimed
    execmany(q, inputs)
    return winnings

def getTickets(username):
    '''def getTickets(username): retrieve all unclaimed tickets owned by given user'''
    q = "SELECT id FROM lottery_tbl WHERE owner=? AND claimed=0"
    inputs = (username, )
    data = execmany(q, inputs).fetchall()
    tickets = {"A": [], "B": [], "C": []}
    for entry in data:
        entry = entry[0]
        if "A" in entry:
            tickets["A"].append(entry)
        elif "B" in entry:
            tickets["B"].append(entry)
        else:
            tickets["C"].append(entry)
    return tickets

def updateTime(username):
    '''def updateTime(username): updates the time of the next daily spin of wheel of fortune'''
    #q="SELECT time FROM user_tbl WHERE username=?"
    #inputs=(username,)
    #time=execmany(q,inputs).fetchone()[0]
    #time=time.split(" ")
    #time[0]=time[0].split("-")
    #time[1]=time[1].split(":")
    #prev=datetime(int(time[0][0]),int(time[0][1]),int(time[0][2]),int(time[1][0]),int(time[1][1]),int(time[1][2]))
    #now=datetime.now()
    #if(now>prev):
    q="UPDATE user_tbl SET time=? WHERE username=?"
    now=datetime.now()+timedelta(days=1)
    now=str(now.strftime("%Y-%m-%d %H:%M:%S"))
    inputs=(now,username)
    execmany(q,inputs)
    return now
    #else:
        #return execmany(q,inputs).fetchone()[0]
