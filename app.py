from flask import flash, redirect, render_template, request, session
import time
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_league_table, get_valid_matches, convert_iso_datetime_to_human_readable, get_insights, find_closest_in_time_matchday_db, group_matches_by_date, process_predictions, find_closest_in_time_match_db_matchday, update_live_matches_and_scores, find_closest_in_time_kickoff_match_db, update_matches_and_scores, find_next_match_db
from models import User, Prediction, Match
from config import app, get_db_session


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/rangliste", methods=["GET", "POST"])
@login_required
def rangliste():
    start_time = time.time()
    try:
        with get_db_session() as db_session:
            # Fetch all matches
            matches = db_session.query(Match).all()

            # Determine matchday_to_display based on session or default to closest matchday
            if request.method == "GET":
                closest_in_time_kickoff_match = find_closest_in_time_kickoff_match_db(db_session)
                matchday_to_display = int(request.args.get('matchday', closest_in_time_kickoff_match.matchday))
                session['matchday_to_display'] = matchday_to_display
            else:
                matchday_to_display = session.get('matchday_to_display')
        
            # Get list of matchdays and formatted matchdays for display
            matchdays_data = sorted(set((match.matchday, match.formatted_matchday) for match in matches))
            matchdays, matchdays_formatted = zip(*matchdays_data)
            
            # Determine next and previous matchdays
            current_index = matchdays.index(matchday_to_display) if matchday_to_display in matchdays else 0
            next_matchday = matchdays[current_index + 1] if current_index + 1 < len(matchdays) else None
            prev_matchday = matchdays[current_index - 1] if current_index > 0 else None

            # Get last update time for display
            last_update = db_session.query(func.max(Match.evaluation_Date)).scalar()
            last_update = convert_iso_datetime_to_human_readable(last_update) if last_update else None

            # Update live matches for live scoring
            update_live_matches_and_scores(db_session)
            
            # Fetch all users sorted by multiple criteria
            users = db_session.query(User).options(
                joinedload(User.predictions)  # Ensures predictions are loaded with users
            ).order_by(
                desc(User.total_points),
                desc(User.correct_result),
                desc(User.correct_goal_diff),
                desc(User.correct_tendency)
            ).all()

            # Fetch matches and predictions for the current matchday
            filtered_matches = db_session.query(Match).filter_by(matchday=matchday_to_display).all()
            filtered_predictions = db_session.query(Prediction).filter_by(matchday=matchday_to_display).all()

            # Calculate user points for the matchday
            user_points_matchday = {user.id: 0 for user in users}
            for prediction in filtered_predictions:
                user_points_matchday[prediction.user_id] += prediction.points

            max_points = max(user_points_matchday.values(), default=0)
            top_users = [user_id for user_id, points in user_points_matchday.items() if points == max_points and max_points != 0]

            match_ids = [match.id for match in filtered_matches]
            index_of_closest_in_time_match = match_ids.index(find_closest_in_time_match_db_matchday(db_session, matchday_to_display).id) + 1 # +1 because loop index in jinja starts at 1
            no_filtered_matches = len(match_ids)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Match to display: ", index_of_closest_in_time_match)
            print(f"Elapsed time for Rangliste: {elapsed_time:.4f} seconds")
                        
            return render_template("rangliste.html",
                                matches=filtered_matches,
                                prev_matchday=prev_matchday,
                                next_matchday=next_matchday,
                                matchday_to_display=matchday_to_display,
                                matchdays_formatted=matchdays_formatted,
                                users=users,
                                user_id=session["user_id"],
                                last_update=last_update,
                                top_users=top_users,
                                user_points_matchday=user_points_matchday,
                                index_of_closest_in_time_match=index_of_closest_in_time_match,
                                no_matches=no_filtered_matches
                                )
        
    except OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return "Database connection error, please try again later.", 500
        

@app.route("/tippen", methods=["GET", "POST"])
@login_required
def tippen():
    try:
        with get_db_session() as db_session:
            # Fetch all matches
            matches = db_session.query(Match).all()

            # Filter valid matches for predictions
            valid_matches = get_valid_matches(matches)

            # Determine matchday_to_display based on session or default to next_matchday
            if request.method == "GET":
                matchday_to_display = int(request.args.get('matchday', find_next_match_db(db_session).matchday))
                session['matchday_to_display'] = matchday_to_display
            else:
                matchday_to_display = session.get('matchday_to_display')

            # Filter matches by matchday parameter or default to closest matchday
            filtered_matches = [match for match in matches if match.matchday == matchday_to_display]

            # Group matches by date
            filtered_matches_by_date = group_matches_by_date(filtered_matches)
            
            # Get list of matchdays and formatted matchdays for display
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
        
    except OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return "Database connection error, please try again later.", 500
    

@app.route("/gruppen")
@login_required
def gruppen():
    try:
        with get_db_session() as db_session:
            table_data = get_league_table(db_session)
            groups = {}

            for team in table_data:
                if team.teamGroupName not in groups:
                    groups[team.teamGroupName] = []

                groups[team.teamGroupName].append(team)

            try:
                del groups["None"]  # To remove the placeholder team
            except KeyError:
                pass

            groups = dict(sorted(groups.items()))

            last_update = table_data[0].lastUpdateTime
            if last_update:
                last_update = convert_iso_datetime_to_human_readable(last_update)
            else:
                last_update = None

            return render_template("gruppen.html", groups=groups, table_data=table_data, last_update=last_update)
    except OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return "Database connection error, please try again later.", 500


@app.route("/regeln")
def regeln():
    return render_template("regeln.html")


@app.route("/")
@login_required
def index():
    try:
        with get_db_session() as db_session:
            return render_template("index.html", insights=get_insights(db_session))
        
    except OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return "Database connection error, please try again later.", 500


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    try:
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

                update_matches_and_scores(db_session)   # TODO updating tables?

                # Redirect user to home page
                return redirect("/")

            # User reached route via GET (as by clicking a link or via redirect)
            else:
                return render_template("login.html")
            
    except OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return "Database connection error, please try again later.", 500
    

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
    try:
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
            
    except OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return "Database connection error, please try again later.", 500
