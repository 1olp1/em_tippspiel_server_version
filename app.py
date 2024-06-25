from flask import flash, redirect, render_template, request, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_matches_db, get_league_table, get_current_datetime_as_object, update_matches_db, update_league_table, is_update_needed_matches, is_update_needed_league_table, update_user_scores, convert_iso_datetime_to_human_readable, get_insights, get_rangliste_data, normalize_datetime
from models import User, Team, Prediction, Match
from config import app, get_db_session

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
    with get_db_session() as db_session:        
        # Get last update to display last update time in html
        last_update = db_session.query(func.max(Match.evaluation_Date)).scalar()
        
        if not last_update:
            last_update = None
        
        else:
            last_update = convert_iso_datetime_to_human_readable(last_update)

        return render_template("rangliste.html",
                            matchdata=get_matches_db(db_session),
                            users=get_rangliste_data(db_session),
                            user_id=session["user_id"],
                            last_update=last_update)


@app.route("/tippen", methods=["GET", "POST"])
@login_required
def tippen():
    with get_db_session() as db_session:
        matches = db_session.query(Match).all()
        valid_matches = []

        for match in matches:
            # Make list of matches that are valid for prediction, e.g. not finished and not started
            if match.matchIsFinished == 0 and get_current_datetime_as_object() < match.matchDateTime:
                valid_matches.append(match)
            
            if match.matchday < 4:
                team_group_name = db_session.query(Team.teamGroupName).filter(Team.id == match.team1_id).first()
                match.teamGroupName = team_group_name[0].replace("Gruppe ", "") if team_group_name else '-'
            else:
                match.teamGroupName = '-'

        if request.method =="POST":
            # Iterate through every match TODO: for match in valid_matches!
            for match in matches:
                match_id = match.id
                matchday = match.matchday

                # Get user predictions for the match
                team1_score = request.form.get(f'team1Score_{match_id}')
                team2_score = request.form.get(f'team2Score_{match_id}')

                # Check for valid input. If it is valid, convert to int. Else, continue to next match iteration
                if team1_score and team2_score:
                    if team1_score.isdigit() and team2_score.isdigit():
                            team1_score = int(team1_score)
                            team2_score = int(team2_score)
                    else:
                        continue
                else:
                    continue

                winner = 1 if team1_score > team2_score else 2 if team1_score < team2_score else 0

                # Get the last prediction for the match
                prediction = db_session.query(Prediction).filter_by(user_id=session["user_id"], match_id=match_id).first()

                # If it exists and differs from the original prediction, update the prediction
                if prediction:
                    if team1_score != prediction.team1_score or team2_score != prediction.team2_score:
                        prediction.team1_score = team1_score
                        prediction.team2_score = team2_score
                        prediction.goal_diff = team1_score - team2_score
                        prediction.winner = winner
                        prediction.prediction_date = get_current_datetime_as_object()
                # If there is no prediction in the db, insert it
                else:
                    new_prediction = Prediction(
                        user_id=session["user_id"],
                        matchday=matchday,
                        match_id=match_id,
                        team1_score=team1_score,
                        team2_score=team2_score,
                        goal_diff=team1_score - team2_score,
                        winner=winner,
                        prediction_date=get_current_datetime_as_object()
                    )
                    db_session.add(new_prediction)
            
            db_session.commit()
    
        # Get all predictions from the user
        predictions = db_session.query(Prediction).filter_by(user_id=session["user_id"]).all()

        # Get time of last update
        last_update = db_session.query(func.max(Match.lastUpdateDateTime)).scalar()
        
        # If an entry for last update exists, format for displaying
        if last_update:
            last_update = convert_iso_datetime_to_human_readable(last_update)

        return render_template("tippen.html", matches=matches, predictions=predictions, valid_matches=valid_matches, last_update=last_update)


@app.route("/gruppen")
@login_required
def gruppen():
    with get_db_session() as db_session:
        table_data = get_league_table(db_session)
        groups = {}

        for team in table_data:
            if team.teamGroupName not in groups:
                groups[team.teamGroupName] = []

            groups[team.teamGroupName].append(team)

        try:
            del groups["None"] # To remove the placeholder team
        except KeyError:
            pass

        groups = dict(sorted(groups.items()))

        last_update = table_data[0].lastUpdateTime
        if last_update:
            last_update = convert_iso_datetime_to_human_readable(last_update)
        else:
            last_update = None

        return render_template("gruppen.html", groups=groups, table_data=table_data, last_update=last_update)


@app.route("/regeln")
def regeln():
    return render_template("regeln.html")

@app.route("/")
@login_required
def index():
    with get_db_session() as db_session:
        return render_template("index.html", insights=get_insights(db_session))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    with get_db_session() as db_session:
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
            user = db_session.query(User).filter_by(username=username).first()

            # Check if user exists and password is correct
            if not user or not check_password_hash(user.hash, password):
                flash("Ungültiger Benutzername und/oder Passwort", 'error')
                return redirect("/login")

            # Remember which user has logged in
            session["user_id"] = user.id
            
            # Update league table and match data if needed
            try:
                if is_update_needed_league_table(db_session):
                    print("Yes. Updating league table...")
                    update_league_table(db_session)
                    print("League table update finished.")

                print("Is update needed for matches?")
                if is_update_needed_matches(db_session):
                    print("Yes. Updating matches database...")
                    update_matches_db(db_session)

                    # Update user scores
                    print("Updating user scores...")
                    update_user_scores(db_session)
                    print("User scores update finished.")
                
                else:
                    print("No update needed")

            except Exception as e:
                print(f"Update failed: {e}")

            update_user_scores(db_session)


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
    with get_db_session() as db_session:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password_repetition = request.form.get("confirmation")

            if not username:
                flash("Kein Benutzername angegeben", 'error')
                return redirect("/register")

            # Check if username already exists
            existing_user = db_session.query(User).filter_by(username=username).first()
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
            db_session.add(new_user)
            db_session.commit()

            # Show success message
            flash("Erfolgreich registriert!", 'success')

            return redirect("/")

        else:
            return render_template("register.html")
