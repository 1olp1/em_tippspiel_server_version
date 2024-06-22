from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_matches, get_league_table, get_current_datetime_str, get_current_datetime_as_object, update_matches_db, update_league_table, is_update_needed_matches, is_update_needed_league_table, update_user_scores, add_up_decimals_to_6, convert_iso_datetime_to_human_readable, get_insights, get_rangliste_data, get_teams, convert_iso_to_datetime_without_decimals
from datetime import datetime, timedelta
from models import User, Base

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Use an absolute path or correct relative path to the SQLite database
DATABASE_URL = 'sqlite:///tippspiel.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session_db = Session()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/rangliste")
@login_required
def rangliste():

    # Get last update to display last update time in html
    last_update = db.execute("""
                             SELECT evaluation_Date FROM matches
                             ORDER BY evaluation_Date DESC
                             LIMIT 1
                             """)[0]["evaluation_Date"]
    
    if not last_update:
        last_update = None
    
    else:
        last_update = convert_iso_datetime_to_human_readable(last_update)

    # Get next kickoff, to be able to display the predictions of users when the match is underway but not yet finished
    next_match = db.execute("""
                              SELECT id, matchDateTime FROM matches
                              WHERE matchIsFinished = 0
                              ORDER BY matchDateTime ASC
                              LIMIT 1
                              """)
    
    if next_match:
        next_match = next_match[0]
        next_match["is_live"] = False

        current_datetime = get_current_datetime_as_object()
        match_start_time = convert_iso_to_datetime_without_decimals(next_match["matchDateTime"]) # Without decimals because API uses kickoff times without decimals
        match_duration = timedelta(minutes=90+15+10)  # Assuming each match lasts 90 minutes
        match_end_time = match_start_time + match_duration

        if match_start_time <= current_datetime <= match_end_time:
            next_match["is_live"] = True

    else:
        next_match = None

    return render_template("rangliste.html",
                           matchdata=get_matches(),
                           users=get_rangliste_data(),
                           user_id=session["user_id"],
                           next_match=next_match,
                           last_update=last_update)


@app.route("/tippen", methods=["GET", "POST"])
@login_required
def tippen():
    matches = get_matches()
    valid_matches = []

    for match in matches:
        # Make list of matches that are valid for prediction, e.g. not finished and not started
        # Also add the group for eacht match for displaying in html
        if match["matchIsFinished"] == 0 and get_current_datetime_str() < match["matchDateTime"]:
           valid_matches.append(match)
        
        if match["matchday"] < 4:
            match["teamGroupName"] = db.execute("SELECT teamGroupName FROM teams WHERE id = ?", match["team1_id"])[0]["teamGroupName"].replace("Gruppe ","")
        else:
            match["teamGroupName"] = '-'

    if request.method =="POST":
        # Iterate through every match
        for match in valid_matches:
            match_id = match["id"]
            matchday = match["matchday"]

            # Get user predictions for the match
            team1_score = request.form.get('team1Score_' + str(match_id))
            team2_score = request.form.get('team2Score_' + str(match_id))

            # Check for valid input. If it is valid, convert to int. Else, continue to next match iteration
            if team1_score and team2_score:
                if team1_score.isdigit() and team2_score.isdigit():
                        team1_score = int(team1_score)
                        team2_score = int(team2_score)
                else:
                    continue
            
            else:
                continue
            
            # Get the last prediction for the match
            prediction = db.execute("SELECT * FROM predictions WHERE user_id = ? AND match_id = ?", session["user_id"], match_id)
            winner = 1 if team1_score > team2_score else 2 if team1_score < team2_score else 0

            # If it exists and differs from the original prediction, update the prediction
            if prediction:
                if team1_score != prediction[0]["team1_score"] or team2_score != prediction[0]["team2_score"]:
                    db.execute("UPDATE predictions SET team1_score = ?, team2_score = ?, goal_diff = ?, winner = ?, prediction_date = ? WHERE user_id = ? AND match_id = ?",
                            team1_score, team2_score, team1_score-team2_score, winner, get_current_datetime_str(), session["user_id"], match_id)

            # If there is no prediction in the db, insert it
            else:
                db.execute("""
                        INSERT INTO predictions (user_id, matchday, match_id, team1_score, team2_score, goal_diff, winner, prediction_date)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        session["user_id"], matchday, match_id, team1_score, team2_score, team1_score-team2_score, winner, get_current_datetime_str())
    
    # Get all predictions from the user
    predictions = db.execute("SELECT * FROM predictions WHERE user_id = ?", session["user_id"])

    # Get time of last update
    last_update = db.execute("""
                                SELECT lastUpdateDateTime FROM matches
                                ORDER BY lastUpdateDateTime DESC
                                LIMIT 1
                                """)[0]["lastUpdateDateTime"]
    
    # If an entry for last update exists, format for displaying
    if last_update:
        last_update = add_up_decimals_to_6(last_update)
        last_update = convert_iso_datetime_to_human_readable(last_update)

    return render_template("tippen.html", matches=matches, predictions=predictions, valid_matches=valid_matches, last_update=last_update)


@app.route("/gruppen")
@login_required
def gruppen():
    table_data = get_league_table()
    groups = {}


    for team in table_data:
        if team["teamGroupName"] not in groups:
            groups[team["teamGroupName"]] = []

        groups[team["teamGroupName"]].append(team)

    try:
        del groups["None"] # To remove the placeholder team
    except KeyError:
        pass

    groups = dict(sorted(groups.items()))

    return render_template("gruppen.html", groups=groups, table_data=table_data)


@app.route("/regeln")
def regeln():
    return render_template("regeln.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html", insights=get_insights())

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username and password were submitted
        if not username or not password:
            flash("Benutzername/Passwort fehlt", "error")
            return redirect("/login")
        
        # Forget any user_id
        session.clear()

        # Query database for username
        user = session_db.query(User).filter_by(username=username).first()

        # Check if user exists and password is correct
        if not user or not check_password_hash(user.hash, password):
            flash("Ungültiger Benutzername und/oder Passwort", 'error')
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = user.id

        print("Is update needed for the league table?")
        try:

            if is_update_needed_league_table():
                print("Yes. Updating...")
                #update_league_table()
                print("Update finished.")

            else:
                print("No update needed.")
        
        except Exception as e:
            print(f"Updating league table failed: {e}")


        
        # Update league table and match data if needed
        """     try:
            if is_update_needed_league_table():
                print("Yes. Updating league table...")
                update_league_table()
                print("League table update finished.")

            if is_update_needed_matches():
                print("Yes. Updating matches database...")
                update_matches_db()

                # Update user scores
                print("Updating user scores...")
                update_user_scores()
                print("User scores update finished.")

        except Exception as e:
            print(f"Update failed: {e}")
            """


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    
    # Message for logging out successfully
    flash("Erfolgreich ausgeloggt!", 'success')

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_repetition = request.form.get("confirmation")

        if not username:
            flash("Kein Benutzername angegeben", 'error')
            return redirect("/register")

        # Check if username already exists
        existing_user = session_db.query(User).filter_by(username=username).first()
        if existing_user:
            flash("Benutzername bereits vergeben", 'error')
            return redirect("/register")

        # Check if passwords are entered and if they match
        if not password or not password_repetition or password != password_repetition:
            flash("Passwörter fehlen oder stimmen nicht überein", 'error')
            return redirect("/register")

        # Hash the password
        hashed_pw = generate_password_hash(password)

        # Create a new User object
        new_user = User(username=username, hash=hashed_pw)

        # Add new user to session and commit to database
        session_db.add(new_user)
        session_db.commit()

        # Show success message
        flash("Erfolgreich registriert!", 'success')

        return redirect("/")

    else:
        return render_template("register.html")
