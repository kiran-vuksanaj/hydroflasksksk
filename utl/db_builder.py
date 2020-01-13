import sqlite3

DB_FILE = "casino.db"

#==========================================================
# EXEC COMMANDS

def exec(cmd):
    '''Executes a sqlite command'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd)
    db.commit()
    return output

def execmany(cmd, inputs):
    '''Executes a sqlite command using ? placeholder'''
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd, inputs)
    db.commit()
    return output

#==========================================================
# BUILD DATABASE WITH ALL NECESSARY TABLES

def build_db():
    '''Creates database if it does not yet exist with the necessary tables'''
    command = "CREATE TABLE IF NOT EXISTS user_tbl (username TEXT, password TEXT, pfp TEXT, money INT, time INT, boosts TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS texas_tbl (game_id TEXT, player TEXT, card1 TEXT, card2 TEXT, card3 TEXT, card4 TEXT, card5 TEXT, bet INT, folded INT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS lottery_tbl (id TEXT, owner TEXT, numbers TEXT, claimed INT)"
    exec(command)
