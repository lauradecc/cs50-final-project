import os

from cs50 import SQL
from flask import Flask, jsonify, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure mail server
app.config["MAIL_USERNAME"] = "cs50laurafinalproject@gmail.com"
app.config["MAIL_PASSWORD"] = "CS50FINALPROJECT"
app.config["MAIL_DEFAULT_SENDER"] = "cs50laurafinalproject@gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
mail = Mail(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Add companies
# db.execute("INSERT INTO companies (name) VALUES(?), (?), (?), (?), (?)", "Key Technology", "Technowire", "Technology Pack", "Monobotics", "Technology Labs")

# All workshops and shows
allWorkshops = ["Handstands", "Juggling", "Aerial Hoop", "Pole Dance", "Acrobatics", "Aerial Silks"]
allShows = ["Circus For Developers Show"]

@app.route("/")
@login_required
def index():
    """Show home page"""

    # Redirect user to index page
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure email was submitted (contains @)
        email = request.form.get("email")
        counter = 0
        for character in email:
            if character == '@':
                counter += 1
        if counter != 1:
            return apology("must provide valid email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 400)

        # Ensure email was submitted (contains @)
        email = request.form.get("email")
        counter = 0
        for character in email:
            if character == '@':
                counter += 1
        if counter != 1:
            return apology("must provide valid email", 400)

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email doesn't exists yet
        if len(rows) != 0:
            return apology("email already registered", 400)

        # Ensure name was submitted
        elif not request.form.get("name"):
            return apology("must provide name", 400)

        # Ensure surname was submitted
        elif not request.form.get("surname"):
            return apology("must provide surname", 400)

        # Ensure company was selected
        elif not request.form.get("company"):
            return apology("must provide company", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Add data to database
        else:
            name = request.form.get("name")
            surname = request.form.get("surname")
            password = request.form.get("password")
            pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            company_id = db.execute("SELECT id FROM companies WHERE name = ?", request.form.get("company"))
            company_id = company_id[0]["id"]
            db.execute("INSERT INTO users (email, name, surname, company_id, hash) VALUES( ?, ?, ?, ?, ? )", email, name, surname, company_id, pw_hash)

        # Query database for new username for automatic log-in after registering
        rows = db.execute("SELECT id FROM users WHERE email = ?", email)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")


    # User reached route via GET
    else:
        # Show company names in form
        companies = db.execute("SELECT name FROM companies")

        # Return registration page
        return render_template("register.html", companies=companies)


@app.route("/workshops", methods=["GET", "POST"])
def workshops():
    """Register/unregister workshops"""

    # User reached route via POST
    if request.method == "POST":

        # Query databases
        workshops = db.execute("SELECT name FROM workshops WHERE user_id = ?", session["user_id"])
        user_data = db.execute("SELECT email, name FROM users WHERE id = ?", session["user_id"])
        email = user_data[0]["email"]
        name = user_data[0]["name"]

        # If already registered
        for workshop in workshops:
            if workshop["name"] in request.form:

                # Redirect user to bookings page
                return redirect("/bookings")

        # Max two workshops per user
        if len(workshops) == 2:
            return apology("two workshops maximum", 400)

        # If not registered yet
        for workshop in allWorkshops:
            if workshop in request.form:

                # Register into database
                db.execute("INSERT INTO workshops (name, user_id) VALUES( ?, ?)", workshop, session["user_id"])

                # Send email confirmation
                sendEmail(workshop, name, email)

                # Redirect to bookings page
                return redirect("/bookings")

    # User reached route via GET
    return render_template("workshops.html")


@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    """Show user bookings"""

    # User reached route via POST
    if request.method == "POST":

        # Query databases
        workshops = db.execute("SELECT name FROM workshops WHERE user_id = ?", session["user_id"])
        user_data = db.execute("SELECT email, name FROM users WHERE id = ?", session["user_id"])
        shows = db.execute("SELECT name FROM shows WHERE user_id = ?", session["user_id"])
        email = user_data[0]["email"]
        name = user_data[0]["name"]

        for workshop in workshops:
            if workshop["name"] in request.form:

                # Delete registration of user for workshop
                db.execute("DELETE FROM workshops WHERE user_id = ? AND name = ?", session["user_id"], workshop["name"])

                # Send cancellation email
                sendCancellationEmail(workshop["name"], name, email)

                # Redirect to bookings page
                return redirect("/bookings")

        for show in shows:
            if show["name"] in request.form:

                # Delete registration of user for workshop
                db.execute("DELETE FROM shows WHERE user_id = ? AND name = ?", session["user_id"], show["name"])

                # Send cancellation email
                sendShowCancellationEmail(name, email)

                # Redirect to bookings page
                return redirect("/bookings")

    # User reached route via GET
    # Obtain data from database
    workshops = db.execute("SELECT name FROM workshops WHERE user_id = ?", session["user_id"])
    shows = db.execute("SELECT name FROM shows WHERE user_id = ?", session["user_id"])

    # Show all activities that the user is registered for
    return render_template("bookings.html", workshops=workshops, shows=shows)


@app.route("/people")
def people():
    people = db.execute("SELECT name, surname FROM users WHERE company_id = (SELECT company_id FROM users WHERE id = ?) AND NOT id = ?", session["user_id"], session["user_id"])
    return jsonify(people)


@app.route("/surprise")
def surprise():
    snacks = [{"surprise": "You will have a free snack to enjoy the show! 🍿🍪🌭🍩🍟🍭\nDon't worry about anything, we will take care of everything!"}]
    return jsonify(snacks)


@app.route("/show", methods=["GET", "POST"])
def show():
    """Register/unregister show"""

    # User reached route via POST
    if request.method == "POST":

        # Query databases
        shows = db.execute("SELECT name FROM shows WHERE user_id = ?", session["user_id"])
        user_data = db.execute("SELECT email, name FROM users WHERE id = ?", session["user_id"])
        email = user_data[0]["email"]
        name = user_data[0]["name"]

        # If already registered
        for show in shows:
            if show["name"] in request.form:

                # Redirect user to bookings page
                return redirect("/bookings")

        # If not registered yet
        for show in allShows:
            if show in request.form:

                # Add to database
                db.execute("INSERT INTO shows (name, user_id) VALUES( ?, ?)", show, session["user_id"])

                # Send email confirmation
                sendShowEmail(name, email)

                # Redirect to bookings page
                return redirect("/bookings")

    # User reached route via GET
    return render_template("show.html")


# Send confirmation email when user registers for workshop
def sendEmail(sport, name, email):
    message = Message(sport + " workshop registration - Circus For Developers", sender = ("Circus For Developers", "cs50laurafinalproject@gmail.com"), recipients=[email])
    message.body = "Hello " + name + "!\n\nYou have successfully registered for the " + sport + " workshop.\n\nWe hope you enjoy it!\n\nCircus For Developers Team 🎪"
    mail.send(message)
    return


def sendCancellationEmail(sport, name, email):
    message = Message(sport + " workshop cancellation - Circus For Developers", sender = ("Circus For Developers", "cs50laurafinalproject@gmail.com"), recipients=[email])
    message.body = "Hello " + name + "!\n\nYour registration for the " + sport + " workshop has been cancelled.\n\nRemember that you can sign up for up to two workshops!\n\nCircus For Developers Team 🎪"
    mail.send(message)
    return


def sendShowEmail(name, email):
    message = Message("Circus For Developers Show registration 🎪", sender = ("Circus For Developers", "cs50laurafinalproject@gmail.com"), recipients=[email])
    message.body = "Hello " + name + "!\n\nYour registration for the Circus For Developers Show is confirmed.\n\nSee you soon!\n\nCircus For Developers Team 🎪"
    mail.send(message)
    return


def sendShowCancellationEmail(name, email):
    message = Message("Circus For Developers Show cancellation 🎪", sender = ("Circus For Developers", "cs50laurafinalproject@gmail.com"), recipients=[email])
    message.body = "Hello " + name + "!\n\nYour cancellation from the Circus For Developers Show has been submited.\n\nWe are sorry to see you go. If you change your mind, let us know!\n\nCircus For Developers Team 🎪"
    mail.send(message)
    return


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

