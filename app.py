from flask import Flask , render_template,request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, os, random
from utl import db_builder, db_manager,carddeck
import urllib3, json, urllib

app = Flask(__name__)
app.secret_key = os.urandom(32)

#====================================================
# FUNCTION WRAPPERS

def login_required(f):
    '''Decorator for making sure user is logged in'''
    @wraps(f)
    def dec(*args, **kwargs):
        '''dec (*args, **kwargs): Decorator for checking login and if user in session'''
        if 'username' in session:
            for arg in args:
                print(arg)
            return f(*args, **kwargs)
        flash('You must be logged in to view this page!', 'alert-danger')
        return redirect('/')
    return dec

def no_login_required(f):
    '''Decorator for making sure user is not logged in'''
    @wraps(f)
    def dec(*args, **kwargs):
        '''dec(*args, **kwargs): Decorator for checking no login'''
        if 'username' not in session:
            return f(*args, **kwargs)
        flash('You cannot view this page while logged in!', 'alert-danger')
        return redirect('/home')
    return dec

#====================================================
# LOGIN AND SIGNUP PAGES

@app.route("/")
def root():
    '''def root(): Redirects to login page if not in session, redirects to home if in session'''
    if 'username' in session: #if logged in
        return redirect('/home')
    return redirect('/login')

@app.route("/login")
@no_login_required
def login():
    '''def login(): login requirement'''
    return render_template('login.html')

@app.route("/auth", methods=["POST"])
@no_login_required
def auth():
    '''def auth(): authenticating login and flashing corresponding errors'''
    enteredU = request.form['username']
    enteredP = request.form['password']
    if(enteredU == "" or enteredP == ""): #if fields empty
        flash('Please fill out all fields!', 'alert-danger')
        return redirect(url_for('login'))
    if (db_manager.userValid(enteredU, enteredP)): #returns true if login successful
        flash('You were successfully logged in!', 'alert-success')
        session['username'] = enteredU
        return redirect(url_for('home'))
    else:
        flash('Wrong Credentials!', 'alert-danger')
        return redirect(url_for('login'))

@app.route("/signup")
@no_login_required
def signup():
    '''def signup(): sign up route, takes in a form for signing up'''
    return render_template("signup.html")

@app.route("/signupcheck", methods=["POST"])
@no_login_required
def signupcheck():
    '''def signupcheck(): Checking if sign up form is filled out correctly; i.e. username taken, passwords match, all fields filled out'''
    username = request.form['username']
    password = request.form['password']
    confirm = request.form['confirmation']
    #preliminary checks on entered fields
    if(username == "" or password == "" or confirm == ""):
        flash('Please fill out all fields!', 'alert-danger')
        return render_template("signup.html", username=username, password=password, confirm=confirm)
    if ("," in username):
            flash('Commas are not allowed in username!', 'alert-danger')
            return render_template("signup.html", username=username, password=password, confirm=confirm)
    if (confirm!=password):
        flash('Passwords do not match!', 'alert-danger')
        return render_template("signup.html", username=username, password=password, confirm=confirm)
    #form information delivered to backend
    added = db_manager.addUser(username,password) #returns True if user was sucessfully added
    if (not added):
        flash('Username taken!', 'alert-danger')
        return render_template("signup.html", username=username, password=password, confirm=confirm)
    flash('You have successfully created an account! Please log in!', 'alert-success')
    return redirect(url_for('login'))

#====================================================
# STARTING HERE THE USER MUST BE LOGGED IN

@app.route("/home")
@login_required
def home():
    '''def home(): homepage checks if user is in session and gets info on user'''
    user = session['username']
    money = db_manager.getMoney(user)
    return render_template("home.html", user=user, home="active", money=money)

@app.route("/profile")
@login_required
def profile():
    '''def profile(): allows user to update their profile and view their purchases'''
    user = session['username']
    return render_template("profile.html", user=user, profile="active")

@app.route("/resetpasswd", methods=["POST"])
@login_required
def password():
    '''def password(): backend of password changes, makes sure form is filled out correctly'''
    password = request.form['password']
    verif = request.form['verif']
    oldpass = request.form['oldpass']
    if (password == "" or verif == "" or oldpass == ""):
        flash("Please fill out all fields!", 'alert-danger')
        return redirect("/profile")
    if (password != verif):
        flash("Passwords do not match!", 'alert-danger')
        return redirect("/profile")
    username = session['username']
    if (not db_manager.userValid(username, oldpass)):
        flash("Wrong password!", 'alert-danger')
        return redirect("/profile")
    db_manager.changePass(username, password)
    flash("Password successfully changed!", 'alert-success')
    return redirect("/home")

@app.route("/store")
@login_required
def store():
    return render_template("store.html", store="active")

@app.route("/games")
@login_required
def games():
    return render_template("games.html", games="active")

#====================================================
# WHEEL OF FORTUNE AND LOTTERY TICKETS

#====================================================
# DICE GAME

#====================================================
# SLOT MACHINE

@app.route("/slotmachine")
@login_required
def slot():
    '''def slot(): placing and checking bets'''
    print("here's bet")
    username = session['username']
    if request.args.get('slotbet'):
        bet = request.args.get('slotbet')
        print(bet)
        if bet == "" or int(bet) < 100 or int(bet) > db_manager.getMoney(username):
            bet = 100
            flash("Please place a valid bet.", 'alert-danger')
            return render_template("slotmachine.html", primarybet = bet, bet = 0, image1 = dict[random.choice(slotImages)], image2 = dict[random.choice(slotImages)], image3 = dict[random.choice(slotImages)], usermoney = db_manager.getMoney(username), money = 0, colour = "yellow", games="active")
        else:
            bet = int(bet)
            db_manager.updateMoney(session['username'], -bet)
            rand1 = random.choice(slotImages)
            rand2 = random.choice(slotImages)
            rand3 = random.choice(slotImages)
            if rand1 == rand2 and rand2 == rand3:
                if rand1 == "lemon":
                     db_manager.updateMoney(session['username'], bet)
                     money = bet
                if rand1 == "cherry":
                     db_manager.updateMoney(session['username'], 2 * bet)
                     money = 2 * bet
                if rand1 == "clover":
                     db_manager.updateMoney(session['username'], 3 * bet)
                     money = 3 * bet
                if rand1 == "heart":
                     db_manager.updateMoney(session['username'], 4 * bet)
                     money = 4 * bet
                if rand1 == "diamond":
                     db_manager.updateMoney(session['username'], 5 * bet)
                     money = 5 * bet
                if rand1 == "dollars":
                     db_manager.updateMoney(session['username'], 6 * bet)
                     money = 6 * bet
                colour = "green"
            else:
                money = 0
                colour = "yellow"
            return render_template("slotmachine.html", primarybet = bet, bet = bet, image1 = dict[rand1], image2 = dict[rand2], image3 = dict[rand3], usermoney = db_manager.getMoney(username), money = money, colour = colour, games="active")
    else:
        bet = 100
        money = 0
        return render_template("slotmachine.html", primarybet = bet, bet = 0, image1 = dict[random.choice(slotImages)], image2 = dict[random.choice(slotImages)], image3 = dict[random.choice(slotImages)], usermoney = db_manager.getMoney(username), money = 0, colour = "yellow", games="active")


def images():
    dict =  {}
    slotImages = []
    list = [35, 25, 20, 10, 6, 4]
    n = 0
    file = open("slotimages.csv", "r") #opens second file with links
    content = file.readlines() #parse through files by line
    content = content[1:len(content)] #take out the table heading
    for line in content:
        line = line.strip() #removes \n
        line = line.split(",") #if line does not contain quotes, split by comma
        dict[line[0]] = (line[1]) #key value pair
        for i in range(list[n]):
            slotImages.append(line[0])
        # print(n)
        # print(list[n])
        n = n + 1
    # print(dict) #testing results
    file.close()
    # print("dict here")
    # print(dict)
    # print("slotimages here")
    # print(slotImages)
    return dict,slotImages

#====================================================
# BLACKJACK

@app.route("/blackjack")
@login_required
def blackjack():
    ''' def blackjack(): route for blackjack game '''
    if   request.method == 'GET':
        # initial entry into a game, show the bet decision page
        mode = 'bet'
        game = {}
    elif 'bet' in request.form:
        # user just made a bet, initialize a new game and deduct bet
        game = {}
        game['bet'] = int(request.form['bet'])
        game['deck'] = cards_api.newdeck()
        game['dealer_cards'] = cards_api.drawcards(game['deck'],2)
        game['player_cards'] = cards_api.drawcards(game['deck'],2)
        db_manager.updateMoney( session['username'], -game['bet'] )
        # TODO: initial blackjack
        mode = 'play'
    elif 'hit' in request.form:
        # user just clicked the "hit" button, give them another card and, if necessary, finish game
        game = session['blackjack']
        newcard = carddeck
        mode = 'play'
    elif 'stand' in request.form:
        # user just clicked the "stand" button, finish game
        game = session['blackjack']

        mode = 'end'

    
    return render_template("blackjack.html",mode=mode,game=game)

#====================================================
# LOGOUT

@app.route("/logout")
@login_required
def logout():
    '''def logout(): logging out of session, redirects to login page'''
    session.clear()
    flash('You were successfully logged out.', 'alert-success')
    return redirect('/')

#====================================================
if __name__ == "__main__":
    db_builder.build_db()
    dict,slotImages = images()
    app.debug = True
    app.run()
