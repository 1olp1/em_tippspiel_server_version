from flask import flash, redirect, render_template, request, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_matches_db, get_league_table, get_valid_matches, update_matches_db, update_league_table, is_update_needed_matches, is_update_needed_league_table, update_user_scores, convert_iso_datetime_to_human_readable, get_insights, get_rangliste_data, find_closest_in_time_matchday_db, group_matches_by_date, process_predictions
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
        # Fetch all matches
        matches = db_session.query(Match).all()

        # Filter valid matches for predictions
        valid_matches = get_valid_matches(matches)

        # Determine matchday_to_display based on session or default to closest matchday
        if request.method == "GET":
            matchday_to_display = int(request.args.get('matchday', find_closest_in_time_matchday_db(db_session)))
            session['matchday_to_display'] = matchday_to_display
        else:
            matchday_to_display = session.get('matchday_to_display')

        # Filter matches by matchday parameter or default to closest matchday
        filtered_matches = [match for match in matches if match.matchday == matchday_to_display]

        # Group matches by date
        filtered_matches_by_date = group_matches_by_date(filtered_matches)
        
        # Get list of matchdays and formatted matchdays
        matchdays_data = sorted(set((match.matchday, match.formatted_matchday) for match in matches))
        matchdays, matchdays_formatted = zip(*matchdays_data)

        # Determine next and previous matchdays
        current_index = matchdays.index(matchday_to_display) if matchday_to_display in matchdays else 0
        next_matchday = matchdays[current_index + 1] if current_index + 1 < len(matchdays) else None
        prev_matchday = matchdays[current_index - 1] if current_index > 0 else None

        if request.method == "POST":
            process_predictions(valid_matches, session, db_session, request)

        # Fetch all predictions for the current user
        predictions = db_session.query(Prediction).filter_by(user_id=session["user_id"]).all()

        # Get time of last match update
        last_update = db_session.query(func.max(Match.lastUpdateDateTime)).scalar()

        # Format last update time for display
        if last_update:
            last_update = convert_iso_datetime_to_human_readable(last_update)

        return render_template('tippen.html', matches=filtered_matches, matchdays=matchdays, matchdays_formatted=matchdays_formatted,
                               next_matchday=next_matchday, prev_matchday=prev_matchday, last_update=last_update,
                               predictions=predictions, valid_matches=valid_matches, matches_by_date=filtered_matches_by_date)


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
                print("Is update needed for league table?")
                if is_update_needed_league_table(db_session):
                    print("/tYes. Updating league table...")
                    update_league_table(db_session)
                    print("/tLeague table update finished.")
                
                else:
                    print("No update needed.")

                print("Is update needed for matches?")
                if is_update_needed_matches(db_session):
                    print("\tYes. Updating matches database...")
                    update_matches_db(db_session)

                    # Update user scores
                    print("\tUpdating user scores...")
                    update_user_scores(db_session)
                    print("\tUser scores update finished.")
                
                else:
                    print("\tNo update needed.")

            except Exception as e:
                print(f"Update failed: {e}")

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
