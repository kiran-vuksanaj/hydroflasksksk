from flask import Flask , render_template,request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, os, random
from utl import db_builder, db_manager,carddeck
import urllib3, json, urllib
import random
import wikipedia

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

rules = {}
if len(rules) == 0:
    print("Retrieving Wikipedia info")
    test = wikipedia.page("Slot machine").content
    rules['slots'] = test[0:374] + " " + test[596:705] + " " + test[1084:1182]
    test = wikipedia.page("Sic bo").content
    rules['dice'] = test[0:324] + " " + test[677:814] + " " + test[832:1071]
    test = wikipedia.summary("Texas hold'em")
    rules['texas'] = test[0:869]
    test = wikipedia.summary("Blackjack")
    rules['blackjack'] = test[0:861]
    test = wikipedia.summary("Roulette")
    rules['roulette'] = test
    test = wikipedia.page("Chinese poker").content
    rules['poker'] = test[0:391] + " " + test[409:513]
else:
    print("All Wikipedia info retrieved.")

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
    tickets = db_manager.getTickets(user)
    notickets = True
    if len(tickets["A"]) + len(tickets["B"]) + len(tickets["C"]) > 0:
        notickets = False
    money = db_manager.getMoney(user)
    return render_template("profile.html", user=user, money=money, notickets=notickets, tickets=tickets.items(), profile="active")

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
    '''def store(): display buying options for user'''
    return render_template("store.html", store="active")

@app.route("/purchase", methods=["POST"])
@login_required
def purchase():
    '''def purchase(): process user's purchase request for lottery tickets'''
    username = session['username']
    type = request.form['type']
    purchased = db_manager.purchaseTicket(username, type)
    if (purchased):
        flash('Purchase successfully made! Navigate to profile to access your ticket!','alert-success')
    else:
        flash('You don\'t have enough money to make this purchase!', 'alert-danger')
    return redirect(url_for("store"))

@app.route("/games")
@login_required
def games():
    '''def games(): displays all games in casino'''
    return render_template("games.html", games="active", slots = rules['slots'], dice = rules['dice'], texas = rules['texas'], blackjack = rules['blackjack'], roulette = rules['roulette'], poker = rules['poker'])

#====================================================
# WHEEL OF FORTUNE

#====================================================
# DICE GAME

@app.route("/dice", methods=["GET", "POST"])
@login_required
def dice():
    '''def dice(): allows user to place bet for dice game'''
    user = session['username']
    if request.method == 'GET':
        money = db_manager.getMoney(user)
        return render_template("dice.html", betting=True, money=money, games="active")
    else:
        bet = int(float(request.form['bet']))
        options = request.form.getlist('options')
        if len(options) == 0 or not db_manager.checkBet(user, bet):
            flash("Please enter a valid bet and choose at least one betting option!", 'alert-danger')
            return redirect(url_for("dice"), code=303)
        u = urllib.request.urlopen("http://roll.diceapi.com/json/3d6")
        response = json.loads(u.read())['dice']
        dice = []
        for roll in response:
            dice.append(roll['value'])
        multiplier = diceH(dice, options)
        amount = multiplier * bet
        db_manager.updateMoney(user, amount)
        lost = False
        if (amount < 0):
            lost=True
            amount *= -1
        money = db_manager.getMoney(user)
        return render_template("dice.html", dice=dice, betting=False, money=money, options=options, bet=len(options)*bet, amount=amount, lost=lost, games="active")

def diceH(dice, options):
    '''def diceH(): helper function to check dice rolls'''
    multiplier = [60, 20, 18, 12, 8, 6, 6, 6, 6, 8, 12, 18, 20, 60]
    sum = 0;
    total_mult = 0
    for die in dice:
        sum += int(die)
    for option in options:
        if option == "big" :
            if sum >= 11 and sum <= 17:
                total_mult += 2
        elif option == "small":
            if sum <= 10 and sum >= 4:
                total_mult += 2
        elif "triple" in option:
            num = option[-1]
            if dice[0] == num and dice[1] == num and dice[2] == num:
                total_mult += 180
        else:
            num = int(option[3:])
            if sum == num:
                total_mult += multiplier[num - 4]
    total_mult -= len(options)
    return total_mult

#====================================================
# ROULETTE

#code to build bulk of roulette betting options
row_one = {}
row_two = {}
row_three = {}
all_rows = {}
file = open("roulette.csv", "r") #opens second file with links
content = file.readlines() #parse through files by line
content = content[1:len(content)] #take out the table heading
for line in content:
    line = line.strip() #removes \n
    line = line.split(",") #if line does not contain quotes, split by comma
    if (line[0] == '1'):
        row_one[line[1]] = (line[2])
    elif (line[0] == '2'):
        row_two[line[1]] = (line[2])
    else:
        row_three[line[1]] = (line[2])
    all_rows[line[1]] = (line[2])
    all_rows['0'] = 'green'
file.close()

@app.route("/roulette", methods=["GET", "POST"])
@login_required
def roulette():
    '''def roulette(): allows user to place bet for roulette game'''
    user = session['username']
    if request.method == 'GET':
        money = db_manager.getMoney(user)
        return render_template("roulette.html", betting=True, money=money, games="active", one=row_one.items(), two=row_two.items(), three=row_three.items())
    else:
        bet = int(float(request.form['bet']))
        options = request.form.getlist('options')
        if len(options) == 0 or not db_manager.checkBet(user, bet):
            flash("Please enter a valid bet and choose at least one betting option!", 'alert-danger')
            return redirect(url_for("roulette"), code=303)
        rand = random.randrange(1, 37)
        multiplier = rouletteH(rand, options)
        amount = multiplier * bet
        db_manager.updateMoney(user, amount)
        lost = False
        if (amount < 0):
            lost=True
            amount *= -1
        money = db_manager.getMoney(user)
        color = all_rows[str(rand)]
        return render_template("roulette.html", betting=False, money=money, options=options, bet=len(options)*bet, amount=amount, lost=lost, result=rand, color=color, games="active")

def rouletteH(result, options):
    total_mult = 0
    for option in options:
        if "single" in option:
            num = int(option[6:])
            if num == result:
                total_mult += 36
        elif "dozen" in option:
            num = int(option[-1])
            if ((num - 1) * 12 + 1) <= result and result <= (num * 12):
                total_mult += 3
        elif option == "1to18":
            if result >= 1 and result <= 18:
                total_mult += 2
        elif option == "19to36":
            if result >= 19 and result <= 36:
                total_mult += 2
        elif option == "even":
            if result % 2 == 0:
                total_mult += 2
        elif option == "odd":
            if result % 2 != 0:
                total_mult += 2
        elif option == "red":
            i = str(result)
            if all_rows[i] == "red":
                total_mult += 2
        else: #black
            i = str(result)
            if all_rows[i] == "black":
                total_mult += 2
    total_mult -= len(options)
    return total_mult

#====================================================
# SLOT MACHINE

@app.route("/slotmachine")
@login_required
def slot():
    '''def slot(): placing and checking bets'''
    username = session['username']
    if request.args.get('slotbet'):
        bet = request.args.get('slotbet')
        if bet == "" or float(bet) < 100 or float(bet) > db_manager.getMoney(username):
            bet = 100
            flash("Please place a valid bet.", 'alert-danger')
            return render_template("slotmachine.html", primarybet = bet, bet = 0, image1 = dict[random.choice(slotImages)], image2 = dict[random.choice(slotImages)], image3 = dict[random.choice(slotImages)], usermoney = db_manager.getMoney(username), money = 0, colour = "#FFD700", games="active", check = "false")
        else:
            bet = int(float(bet))
            db_manager.updateMoney(session['username'], -bet)
            rand1 = random.choice(slotImages)
            rand2 = random.choice(slotImages)
            rand3 = random.choice(slotImages)
            random.shuffle(slots)
            images = [dict[slots[0]], dict[slots[1]], dict[slots[2]], dict[slots[3]], dict[slots[4]], dict[slots[5]]]
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
                colour = "#FFD700"
            return render_template("slotmachine.html", primarybet = bet, bet = bet, image1 = dict[rand1], image2 = dict[rand2], image3 = dict[rand3], usermoney = db_manager.getMoney(username), money = money, colour = colour, games="active", check = "true", images = images)
    else:
        bet = 100
        money = 0
        return render_template("slotmachine.html", primarybet = bet, bet = 0, image1 = dict[random.choice(slotImages)], image2 = dict[random.choice(slotImages)], image3 = dict[random.choice(slotImages)], usermoney = db_manager.getMoney(username), money = 0, colour = "#FFD700", games="active", check = "false")

dict = {}
slotImages = []
slots = []
list = [35, 25, 20, 10, 6, 4]
n = 0
file = open("slotimages.csv", "r") #opens second file with links
content = file.readlines() #parse through files by line
content = content[1:len(content)] #take out the table heading
for line in content:
    line = line.strip() #removes \n
    line = line.split(",") #if line does not contain quotes, split by comma
    dict[line[0]] = (line[1]) #key value pair
    slots.append(line[0])
    for i in range(list[n]):
        slotImages.append(line[0])
    n = n + 1
file.close()

#====================================================
# SCRATCH TICKET

@app.route("/lottery", methods=["GET", "POST"])
@login_required
def lotto():
    '''def lotto(): scratch ticket generator and handles lotto transactions'''
    username = session['username']
    x=["307px","201px","95px","307px","201px","95px","307px","201px","95px","307px","201px","95px"]
    y=["270px","270px","270px", "340px", "340px","340px","415px","415px","415px","485px","485px","485px"]
    loop=[0,1,2,3,4,5,6,7,8,9,10,11]
    if request.method == 'GET': #scratch the ticket
        if request.args.get("id"):
            id = request.args.get("id")
            valid = db_manager.checkId(id)
            if valid:
                claimed = db_manager.getClaimed(id) #check if ticket has been claimed already
                if claimed:
                    flash("This ticket has been redeemed already. You have been redirected to the store.", 'alert-primary')
                    return redirect(url_for("store"))
                num = db_manager.getNum(id)
                for i in range(len(num)):
                    if(num[i]==1):
                        num[i]="one.png"
                    if(num[i]==2):
                        num[i]="two.png"
                    if(num[i]==3):
                        num[i]="three.png"
                    if(num[i]==4):
                        num[i]="four.png"
                    if(num[i]==5):
                        num[i]="five.png"
                    if(num[i]==6):
                        num[i]="six.png"
                    if(num[i]==7):
                        num[i]="seven.png"
                    if(num[i]==8):
                        num[i]="eight.png"
                    if(num[i]==9):
                        num[i]="nine.png"
                    if(num[i]==0):
                        num[i]="zero.png"
                type = db_manager.getType(id)
                return render_template("lottery.html",xpos=x,ypos=y,id=id,type=type,numbers=num,index=loop,usermoney=db_manager.getMoney(username),store="active")
            else: #invalid id
                flash("Invalid ID for lottery ticket. You have been redirected to the store.", 'alert-danger')
                return redirect(url_for('store'))
        else: #no id
            flash("No ID was provided for lottery ticket. You have been redirected to the store.", 'alert-danger')
            return redirect(url_for('store'))
    else: #claim prizes
        id = request.args.get('id')
        claimed = db_manager.getClaimed(id) #check if ticket has been claimed already
        if claimed:
            flash("Your prize has been claimed already. You have been redirected to the store.", 'alert-primary')
            return redirect(url_for("store"))
        else:
            num = db_manager.getNum(id)
            for i in range(len(num)):
                if(num[i]==1):
                    num[i]="one.png"
                if(num[i]==2):
                    num[i]="two.png"
                if(num[i]==3):
                    num[i]="three.png"
                if(num[i]==4):
                    num[i]="four.png"
                if(num[i]==5):
                    num[i]="five.png"
                if(num[i]==6):
                    num[i]="six.png"
                if(num[i]==7):
                    num[i]="seven.png"
                if(num[i]==8):
                    num[i]="eight.png"
                if(num[i]==9):
                    num[i]="nine.png"
                if(num[i]==0):
                    num[i]="zero.png"
            winnings = db_manager.claimPrize(username, id)
            if(winnings == 0):
                flash("No winnings. Better luck next time!",'alert-danger')
            else:
                flash("Congratulations! You have claimed $" + str(winnings) + "!", 'alert-success')
            return render_template("lottery.html",xpos=x,ypos=y,numbers=num,index=loop,prizes=True,usermoney=db_manager.getMoney(session['username']),store="active")
#====================================================
# BLACKJACK

def blackjack_cardtotal(cards):
    '''def cardtotal(cards): calculate blackjack value of list of cards '''
    total = 0
    aces = 0
    for card in cards:
        if card['value'] == 'ACE':
            aces += 1
            total += 11
        else:
            try:
                value = int(card['value'])
            except ValueError:
                # value for all face cards is 10
                value = 10
            total += value
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

@app.route("/blackjack",methods=['GET','POST'])
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
        game['bet'] = int(float(request.form['bet']))
        game['deck'] = carddeck.newdeck()
        game['dealer_cards'] = carddeck.drawcards(game['deck'],2)
        game['player_cards'] = carddeck.drawcards(game['deck'],2)
        db_manager.updateMoney( session['username'], -game['bet'] )
        print(game['dealer_cards'])
        # TODO: initial blackjack
        mode = 'play'
    elif 'hit' in request.form:
        # user just clicked the "hit" button, give them another card and, if necessary, finish game
        game = session['blackjack']
        newcard = carddeck.drawcards(game['deck'],1)
        game['player_cards'] += newcard
        if blackjack_cardtotal(game['player_cards']) > 21:
            flash('Bust','alert-danger')
            mode = 'end'
        else:
            mode = 'play'
    elif 'stand' in request.form:
        # user just clicked the "stand" button, finish game
        game = session['blackjack']
        # play dealer's part
        player_total = blackjack_cardtotal(game['player_cards'])
        dealer_total = blackjack_cardtotal(game['dealer_cards'])
        while dealer_total < 17:
            game['dealer_cards'] += carddeck.drawcards(game['deck'],1)
            print('card drawn for dealer: ',game['dealer_cards'][-1]['code'])
            dealer_total = blackjack_cardtotal( game['dealer_cards'] )
        if dealer_total > 21:
            flash('Dealer Bust! You Win!','alert-success')
            db_manager.updateMoney( session['username'], 2*game['bet'] )
        elif player_total > dealer_total:
            flash('You Win!','alert-success')
            db_manager.updateMoney( session['username'], 2*game['bet'] )
        elif player_total == dealer_total:
            flash('Push (tie)','alert-info')
            db_manager.updateMoney( session['username'], game['bet'] )
        else:
            flash('You lose.','alert-danger')
        mode = 'end'

    if mode == 'end':
        del session['blackjack']
    else:
        session['blackjack'] = game

    return render_template("blackjack.html",mode=mode,game=game,games="active")

#====================================================
# TEXAS HOLDEM
@app.route("/holdem")
@login_required
def holdem():
    ''' def holdem(): renders texas holdem game selector for players who have not joined a game, renders game for players in a game '''
    game_id = db_manager.current_game(session['username'])
    if(game_id):
        # if game id exists, then the user is in a game and said game should be rendered
        return render_template("holdem_game.html")
    else:
        # if game id is 0, then the game selection page should be rendered

        return render_template("holdem_lobby.html")
    return 'yikes'

@app.route("/holdem/join",methods=['GET'])
@login_required
def join_holdemgame():
    if not 'game_id' in request.args or request.args['game_id'] == '':
        flash('please choose a game to join!','alert-danger')
        return redirect(url_for('holdem'))
    game_id = request.args['game_id']
    cards = carddeck.drawcards(game_id,2)
    db_manager.addplayer(game_id,username,cards)
    flash('You [{}] have successfully joined game {}'.format(username,game_id),'alert-success')
    return redirect(url_for('holdem'))


@app.route("/holdem/create")
@login_required
def create_holdem():
    ''' def create_holdem(): create a new texas holdem game '''
    game_id = carddeck.newdeck()
    # add 'board' player to game
    board_cards = carddeck.drawcards(game_id,5)
    db_manager.addplayer(game_id,'board',board_cards)
    #add first player to game
    player_cards = carddeck.drawcards(game_id,2)
    db_manager.addplayer(game_id,session['username'],player_cards)

    flash('game successfully created.','alert-success')

    return redirect(url_for('holdem'))


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
    app.debug = True
    app.run()
