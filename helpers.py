from flask import flash, redirect, session
from sqlalchemy import func, text, desc, asc
from functools import wraps
import requests
import uuid
import os
from PIL import Image
from datetime import datetime
from models import User, Match, Team, Prediction
from collections import defaultdict

# Prepare API requests
league = "em"      # bl1 for 1. Bundesliga
league_id = 4708
season = "2024"     # 2023 for 2023/2024 season

# urls for openliga queries
url_matchdata = f"https://api.openligadb.de/getmatchdata/{league}/{season}"
url_table = f"https://api.openligadb.de/getbltable/{league}/{season}"
url_teams = f"https://api.openligadb.de/getavailableteams/{league}/{season}"

# Folder paths
local_folder_path = os.path.join(".", "static", league, season)
img_folder =  os.path.join(local_folder_path, "team-logos")

# Dummy team info
dummy_team_id = 5251


def get_matches_db(db_session):
        return db_session.query(Match).all()


def get_teams(db_session):
    return db_session.query(Team).all()


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def make_image_filepath(team):
    img_file_name = team['shortName'] + os.path.splitext(team['teamIconUrl'])[1]
    img_file_path = os.path.join(img_folder, img_file_name)

    return img_file_path


def get_openliga_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        return response.json()
    
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return None
    

def get_league_table(db_session):        
    return db_session.query(Team).order_by(Team.teamRank.asc()).all()
        

def insert_teams_to_db(db_session):
    print("Inserting teams to db")
    try:
        teams = get_openliga_json(url_teams)
        if teams:
            for team in teams:
                team = Team(
                    id = team["teamId"],
                    teamName = team["teamName"],
                    shortName = team["shortName"],
                    teamIconUrl = team["teamIconUrl"],
                    teamIconPath = make_image_filepath(team),
                    teamGroupName = team["teamGroupName"]
                )
                db_session.add(team)

            # Insert dummy team for open matchups after the group stage where teams are yet undetermined
            dummy_team = Team(
                id = dummy_team_id,
                teamName = '-',
                shortName = '-',
                teamIconPath = os.path.join(img_folder,"dummy-teamlogo.png")
            )

            db_session.add(dummy_team)

            # Download and resize team icon images
            print("Downloading and resizing team icon images")
            download_and_resize_logos(teams)
            
            db_session.query(Team).update({Team.lastUpdateTime: get_current_datetime_str()})
        db_session.commit()
    except Exception as e:
            print(f"Updating inserting teams failed: {e}")
               

def update_league_table(db_session):
    table = get_openliga_json(url_table)
    if table:
        for teamRank, team in enumerate(table, start=1):

            db_session.query(Team).filter_by(id=team["teamInfoId"]).update({
                Team.points: team["points"],
                Team.opponentGoals: team["opponentGoals"],
                Team.goals: team["goals"],
                Team.matches: team["matches"],
                Team.won: team["won"],
                Team.lost: team["lost"],
                Team.draw: team["draw"],
                Team.goalDiff: team["goalDiff"],
                Team.teamRank: teamRank
            })
        # Update lastUpdateTime for all teams
        db_session.query(Team).update({Team.lastUpdateTime: get_current_datetime_str()})

        # Commit the session to persist data
        db_session.commit()


def update_user_scores(db_session):
    # Get data for evaluating the predictions
    matches = get_matches_db(db_session)
    
    for match in matches:
        if match.matchIsFinished == 1 and match.predictions_evaluated == 0:
            # Calculate match outcome parameters
            team1_score = match.team1_score
            team2_score = match.team2_score
            goal_diff = team1_score - team2_score
            winner = 1 if team1_score > team2_score else 2 if team1_score < team2_score else 0

            # Get predictions for this match
            predictions = db_session.query(Prediction).filter(Prediction.match_id == match.id).all()

            for prediction in predictions:
                if team1_score == prediction.team1_score and team2_score == prediction.team2_score:
                    prediction.points = 4
                elif goal_diff == prediction.goal_diff and winner != 0:
                    prediction.points = 3
                elif winner == prediction.winner or goal_diff == prediction.goal_diff and winner == 0:
                    prediction.points = 2
                else:
                    prediction.points = 0

            # Update match evaluation status
            match.predictions_evaluated = 1
            match.evaluation_Date = get_current_datetime_as_object()

    # Update total points in the users table (Query with help from chatGPT)
    users = db_session.query(User).all()

    # Update total_points for each user
    for user in users:
        # Update user total points
        user.total_points = db_session.query(func.sum(Prediction.points)).filter(Prediction.user_id == user.id).scalar() or 0

        # Correct predictions with 4 points
        user.correct_result = db_session.query(func.count()).filter(Prediction.points == 4, Prediction.user_id == user.id).scalar() or 0

        # Correct goal diff predictions 3 points
        user.correct_goal_diff = db_session.query(func.count()).filter(Prediction.points == 3, Prediction.user_id == user.id).scalar() or 0

        # Correct tendency predictions 2 points
        user.correct_tendency = db_session.query(func.count()).filter(Prediction.points == 2, Prediction.user_id == user.id).scalar() or 0

    # Commit all changes to the database
    db_session.commit()


def get_valid_matches(matches):
    return [match for match in matches
            if match.matchIsFinished == 0 and get_current_datetime_as_object() < match.matchDateTime]


def process_predictions(valid_matches, session, db_session, request):
    prediction_added = False
    
    # Iterate through valid matches and process predictions
    for match in valid_matches:
        match_id = match.id

        # Retrieve user input for team scores
        team1_score = request.form.get(f'team1Score_{match_id}')
        team2_score = request.form.get(f'team2Score_{match_id}')
        print(f'Match ID: {match_id}, Team 1 Score: {team1_score}, Team 2 Score: {team2_score}')

        # Retrieve or create prediction entry
        prediction = db_session.query(Prediction).filter_by(user_id=session["user_id"], match_id=match_id).first()

        # If prediction existed, but input fields were posted empty, then delete the prediction
        if prediction and not team1_score and not team2_score:
            db_session.delete(prediction)
            prediction_added = True
            continue

        # Validate and convert scores to integers
        if team1_score and team2_score and team1_score.isdigit() and team2_score.isdigit():
            team1_score = int(team1_score)
            team2_score = int(team2_score)
        else:
            continue

        # Determine winner based on scores
        winner = 1 if team1_score > team2_score else 2 if team1_score < team2_score else 0

        if prediction:
            # Update existing prediction if changed
            if team1_score != prediction.team1_score or team2_score != prediction.team2_score:
                prediction.team1_score = team1_score
                prediction.team2_score = team2_score
                prediction.goal_diff = team1_score - team2_score
                prediction.winner = winner
                prediction.prediction_date = get_current_datetime_as_object()
                prediction_added = True
        else:
            # Create new prediction if none exists
            new_prediction = Prediction(
                user_id=session["user_id"],
                matchday=match.matchday,
                match_id=match_id,
                team1_score=team1_score,
                team2_score=team2_score,
                goal_diff=team1_score - team2_score,
                winner=winner,
                prediction_date=get_current_datetime_as_object()
            )
            db_session.add(new_prediction)
            prediction_added = True

    # Commit changes if predictions were added
    if prediction_added:
        db_session.commit()
        flash("Tipps erfolgreich gespeichert.", "success")
    else:
        flash("Keine Änderungen oder Tipps fehlerhaft.", "warning")


def insert_matches_to_db(db_session):
    # Query openliga API with link from above
    matchdata = get_openliga_json(url_matchdata)

    if matchdata:
        for match in matchdata:
            # Local variable if match is finished
            matchFinished = match["matchIsFinished"]

            team1_score = match["matchResults"][1]["pointsTeam1"] if matchFinished else None
            team2_score = match["matchResults"][1]["pointsTeam2"] if matchFinished else None

            match = Match(
                id = match["matchID"],
                matchday = match["group"]["groupOrderID"],
                team1_id = match["team1"]["teamId"],
                team2_id = match["team2"]["teamId"],
                team1_score = team1_score,
                team2_score = team2_score,
                matchDateTime = match["matchDateTime"],
                matchIsFinished = matchFinished,
                location = match["location"]["locationCity"],
                lastUpdateDateTime = match["lastUpdateDateTime"]
            )
            
            db_session.add(match)

    db_session.commit()


def download_and_resize_logos(teams):
    # Make path for team logos if it does not already exist for the league and season
    os.makedirs(img_folder, exist_ok=True)

    # If folder empty, download images
    if not os.listdir(img_folder):      
        for team in teams:
            try:
                img_url = team['teamIconUrl']
                response = requests.get(
                    img_url,
                    cookies={"session": str(uuid.uuid4())},
                    headers={"Accept": "*/*", "User-Agent": "python-requests"},
                )
                response.raise_for_status()

                # Create image paths
                img_file_path = make_image_filepath(team)

                # Save images
                with open(img_file_path, 'wb') as f:
                    f.write(response.content)
                
                # Lower resolution
                resize_image(img_file_path)

            except (KeyError, IndexError, requests.RequestException, ValueError):
                return None


def get_insights(db_session):
    user_id = session["user_id"]

    # Predictions rated
    predictions_rated = db_session.query(func.count(Prediction.id).label('predictions_rated'))\
        .join(Match, Match.id == Prediction.match_id)\
        .filter(Prediction.user_id == user_id, Match.matchIsFinished == 1)\
        .scalar()

    # Prediction count
    prediction_count = db_session.query(func.count(Prediction.id).label('prediction_count'))\
        .filter(Prediction.user_id == user_id)\
        .scalar()

    # Finished matches
    finished_matches = db_session.query(func.count(Match.id).label('completed_matches'))\
        .filter(Match.matchIsFinished == 1)\
        .scalar()

    # Total points of the user
    total_points_user = db_session.query(User.total_points).filter(User.id == user_id).scalar()

    # User rank
    subquery = db_session.query(
        User.id,
        func.row_number().over(order_by=User.total_points.desc()).label('rank')
    ).subquery()

    rank = db_session.query(subquery.c.rank).filter(subquery.c.id == user_id).scalar()

    # Base statistics for the user
    base_stats = db_session.query(User.correct_result, User.correct_goal_diff, User.correct_tendency)\
        .filter(User.id == user_id).first()

    # Number of users
    no_users = db_session.query(func.count(User.id).label('no_users')).scalar()

    # Store the statistics in the insights dictionary
    insights = {}

    # If there have been predictions, count how many were made
    if predictions_rated:
        insights["predictions_rated"] = predictions_rated
    else:
        insights["predictions_rated"] = 0

    # Create useful statistics and store in insights dict    
    insights["total_games_predicted"] = prediction_count
    insights["missed_games"] = finished_matches - predictions_rated    
    insights["total_points"] = total_points_user
    insights["username"] = db_session.query(User.username).filter(User.id == user_id).scalar()
    insights["no_users"] = no_users
    insights["rank"] = rank
    insights["corr_result"] = base_stats.correct_result
    insights["corr_goal_diff"] = base_stats.correct_goal_diff
    insights["corr_tendency"] = base_stats.correct_tendency
    insights["wrong_predictions"] = insights["predictions_rated"] - insights["corr_result"] - insights["corr_goal_diff"] - insights["corr_tendency"]

    # Differentiate if predictions have been rated to avoid dividing by 0 for the percentage
    if insights["predictions_rated"] != 0:
        insights["corr_result_p"] = round((base_stats.correct_result / insights["predictions_rated"])*100)
        insights["corr_goal_diff_p"] = round(base_stats.correct_goal_diff / insights["predictions_rated"]*100)
        insights["corr_tendency_p"] = round(base_stats.correct_tendency / insights["predictions_rated"]*100)
        insights["wrong_predictions_p"] = round(insights["wrong_predictions"] / insights["predictions_rated"]*100) 
        insights["points_per_tip"] = round(total_points_user / insights["predictions_rated"], 2)
    else:
        insights["corr_result_p"] = 0
        insights["corr_goal_diff_p"] = 0
        insights["corr_tendency_p"] = 0
        insights["wrong_predictions_p"] = 0
        insights["points_per_tip"] = 0

    return insights


def is_update_needed_league_table(db_session):
    # If table is empty, fill teams table
    empty_check_db = db_session.query(Team).all()

    if not empty_check_db:
        print("teams table is empty, inserting teams first...")
        insert_teams_to_db(db_session)
        print("inserting done.")

    # Get current matchday by online query (returns the upcoming matchday after the middle of the week)
    current_matchday = get_current_matchday_openliga()

    # Get current matchday of the local database
    current_match_db = db_session.query(Team.matches, Team.lastUpdateTime).order_by(Team.matches.desc()).first()
    
    if current_matchday > current_match_db.matches:
        return True

    # Last update times if the matchday is equal
    else:
         # Get last update time of the online matchdata
        lastUpdateTime_openliga = get_last_online_change(current_matchday)

        lastUpdateTime_db = current_match_db.lastUpdateTime
        
        if lastUpdateTime_db:
            # Convert dates to comparable format
            lastUpdateTime_openliga = normalize_datetime(lastUpdateTime_openliga)
            lastUpdateTime_db = normalize_datetime(lastUpdateTime_db)

            # If online data is more recent, update the database
            if lastUpdateTime_openliga > lastUpdateTime_db:
                return True
            
            else:
                return False
            
        else:
            # When there are no comparable update times, update anyway to be on the safe side
            return True


def is_update_needed_matches(db_session):
    # If matches table is empty, fill matches table
    empty_check_db = db_session.query(Match).all()

    if not empty_check_db:
        print("\tMatches table is empty, inserting matches first...")
        insert_matches_to_db(db_session) 
        print("\tInserting done.")
        print("\tUpdating user scores.")
        update_user_scores(db_session)
        print("\tUser scores updated.")

    # Get current matchday from API and DB (gets the closest in time matchday (also past matches are considered))
    current_matchday_API = get_current_matchday_openliga()
    current_matchday_data_db = find_closest_in_time_match_db(db_session)

    # Get matchday and id from db based on the former query
    current_matchday_db = current_matchday_data_db.matchday
    current_matchday_id_db = current_matchday_data_db.id

    # Print to enable debugging for comparison of matchdays
    print("\tCurrent matchday local: ", current_matchday_db)
    print("\tCurrent matchday API: ", current_matchday_API)

    ### Compare matchdays and if they're the same check for update times
    if current_matchday_db < current_matchday_API:
        return True
    
    # If the next matchdays are the same, check for last update times
    elif current_matchday_db == current_matchday_API:

        # Get last online update for the match
        lastUpdateTime_openliga = get_last_online_change(current_matchday_API)

        # Get last update time of the locally saved db
        last_update_time_db = db_session.query(Match.lastUpdateDateTime).filter_by(id=current_matchday_id_db).scalar()
        
        # If a last update time exists for the next match
        if last_update_time_db and lastUpdateTime_openliga:
            # Convert dates to comparable format
            lastUpdateTime_openliga = normalize_datetime(lastUpdateTime_openliga)
            last_update_time_db = normalize_datetime(last_update_time_db)

            # If online data is more recent, update the database
            print("\tLast update time openliga:", lastUpdateTime_openliga)
            print("\tLast update time db:", last_update_time_db)
            if lastUpdateTime_openliga > last_update_time_db:
                return True
            
            else:
                return False
            
        else:
            # When there are no comparable update times, update anyway to be on the safe side
            return True
        
    else:
        False


def update_matches_db(db_session):
    # Get unfinished matches of the local database
    unfinished_matches_db = db_session.query(Match).filter(Match.matchIsFinished == 0).all()

    for unfinished_match in unfinished_matches_db:
        # Get matchdata openliga
        matchdata_openliga = get_matchdata_openliga(unfinished_match.id)

        # Get lastUpdateTimes openliga and db
        last_update_time_openliga = matchdata_openliga["lastUpdateDateTime"]
        last_update_time_db = unfinished_match.lastUpdateDateTime

        if last_update_time_openliga and last_update_time_db:
            # Convert dates to comparable format
            last_update_time_openliga = normalize_datetime(last_update_time_openliga)

            if last_update_time_openliga > last_update_time_db:
                update_match_in_db(matchdata_openliga, db_session)
        else:
            # Update if last update time is missing or inconsistent
            update_match_in_db(matchdata_openliga, unfinished_match, db_session)


def update_match_in_db(matchdata_API, match_db, db_session):
    print("Updating match: ", matchdata_API["matchID"])
    # Local variable if match is finished to distinguish team_scores
    matchFinished = matchdata_API["matchIsFinished"]

    # Prepare update dictionary
    update_data = {
        Match.matchDateTime: matchdata_API["matchDateTime"],
        Match.matchIsFinished: matchFinished,
        Match.lastUpdateDateTime: matchdata_API["lastUpdateDateTime"]
    }

    # If teams were not yet determined, update team_id's    
    if match_db.team1_id == dummy_team_id or match_db.team2_id == dummy_team_id:
        update_data[Match.team1_id] = matchdata_API["team1"]["teamID"]
        update_data[Match.team2_id] = matchdata_API["team2"]["teamID"]

    # Conditionally update team scores based on match finished status
    if matchFinished:
        update_data[Match.team1_score] = matchdata_API["matchResults"][1]["pointsTeam1"]
        update_data[Match.team2_score] = matchdata_API["matchResults"][1]["pointsTeam2"]

    db_session.query(Match).filter_by(id=matchdata_API["matchID"]).update(update_data)

    # Commit the session to persist data
    db_session.commit()


def get_matchdata_openliga(id):
    url = f"https://api.openligadb.de/getmatchdata/{id}"

    matchdata = get_openliga_json(url)

    return matchdata


def get_last_online_change(matchday):
    # Make url to get last online change
    url = f"https://api.openligadb.de/getlastchangedate/{league}/{season}/{matchday}"

    # Query API and convert to correct format
    # (to ensure that the datetime module works correctly)
    online_change = add_up_decimals_to_6(get_openliga_json(url))

    return online_change

def get_current_matchday_openliga():
    # Openliga DB API
    url = f"https://api.openligadb.de/getcurrentgroup/{league}"

    # Query API
    current_matchday = get_openliga_json(url)

    if current_matchday:
        return current_matchday["groupOrderID"]

    return None


def resize_image(image_path, max_size=(100, 100)):
    """ For faster load times of the page, it is useful to lower the resolution of the pictures """
    if image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        # Open the image
        with Image.open(image_path) as f:
            # Resize the image while maintaining the aspect ratio
            f.thumbnail(max_size)

            # Save the resized image to the output folder
            f.save(image_path)


def get_rangliste_data(db_session, matchday):
    # Query users and their predictions
    users_predictions = (
        db_session.query(User, Prediction)
        .outerjoin(Prediction, User.id == Prediction.user_id)
        .filter_by(matchday=matchday)
        .order_by(desc(User.total_points), desc(User.correct_result), desc(User.correct_goal_diff), desc(User.correct_tendency), asc(Prediction.matchday))
        .all()
    )

    # Process the query results
    user_predictions = {}
    for user, prediction in users_predictions:
        if user.id not in user_predictions:
            user_predictions[user.id] = {
                'username': user.username,
                'id': user.id,
                'total_points': user.total_points,
                'correct_result': user.correct_result,
                'correct_goal_diff': user.correct_goal_diff,
                'correct_tendency': user.correct_tendency,
                'predictions': []
            }

        if prediction:
            user_predictions[user.id]['predictions'].append({
                'matchday': prediction.matchday,
                'match_id': prediction.match_id,
                'team1_score': prediction.team1_score,
                'team2_score': prediction.team2_score,
                'points': prediction.points
            })

    user_predictions_list = list(user_predictions.values())
    return user_predictions_list


def add_up_decimals_to_6(date_string):
    # Format dates of the API to make them usable with the datetime module. Intended to use with ISO formatted dates
    split_string = date_string.split('.')

    pre_decimals = split_string[0]
    decimals = split_string[1]

    while len(decimals) < 6:
        decimals += "0"
        
    return f"{pre_decimals}.{decimals}"

def get_current_datetime_str():
    # Format the current date and time as a string in the desired format
    return datetime.now().isoformat()


def get_current_datetime_as_object():
    # Format the current date and time as a string in the desired format
    return datetime.now()


def convert_iso_datetime_to_human_readable(iso_string_or_datetime_obj):
    if isinstance(iso_string_or_datetime_obj, str):
        date = datetime.fromisoformat(iso_string_or_datetime_obj)
    else: 
        date = iso_string_or_datetime_obj

    weekday_names = ["Mo.", "Di.", "Mi.", "Do.", "Fr.", "Sa.", "So."]

    # Format the datetime object into a more readable format
    match_time_readable = f"{weekday_names[date.weekday()]} {date.strftime('%d.%m.%Y %H:%M')}"
    return match_time_readable


# With help from chatgpt
def normalize_datetime(input_dt):
    # Define possible datetime string formats
    datetime_formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]

    if isinstance(input_dt, str):
        dt = None
        for fmt in datetime_formats:
            try:
                dt = datetime.strptime(input_dt, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            raise ValueError(f"Time data '{input_dt}' does not match any expected format")
    elif isinstance(input_dt, datetime):
        dt = input_dt
    else:
        raise ValueError("Input must be a datetime string or a datetime object")

    # Remove microseconds
    dt_without_microseconds = dt.replace(microsecond=0)
    return dt_without_microseconds


def find_closest_in_time_match_db(db_session):
    # Get current match from db based on which match is closest in time
    current_datetime = datetime.now()
    
    current_matchday_data_db = db_session.query(
        Match.matchday,
        Match.id
    ).order_by(
        func.abs(func.timestampdiff(text('SECOND'), Match.matchDateTime, current_datetime))
    ).first()           # Query by chatgpt

    return current_matchday_data_db


def find_closest_in_time_matchday_db(db_session):
    return find_closest_in_time_match_db(db_session).matchday



def find_next_matchday_db(db_session):
    # Get current datetime
    current_datetime = datetime.now()

    # Subquery to find the minimum positive time difference
    subquery = db_session.query(
        func.min(Match.matchDateTime - current_datetime).label('min_diff')
    ).filter(
        Match.matchDateTime > current_datetime
    ).scalar_subquery()

    # Query to retrieve the closest future match
    next_matchday_db = db_session.query(
        Match.matchday
    ).filter(
        Match.matchDateTime == current_datetime + subquery  # Adjust to use the subquery result
    ).first()

    return next_matchday_db.matchday


def group_matches_by_date(matches):
    matches_by_date = defaultdict(list)
    for match in matches:
        match_date = match.formatted_matchDate
        matches_by_date[match_date].append(match)
    return matches_by_date