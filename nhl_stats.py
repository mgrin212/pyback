
from flask import Flask, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def get_nhl_data():
    # Define the NHL API endpoint
    endpoint = "https://statsapi.web.nhl.com/api/v1/schedule?expand=schedule.linescore,schedule.scoringplays"

    # Make a request to the NHL API
    response = requests.get(endpoint)

    # Parse the JSON response
    if response.status_code == 200:
        data = response.json()
    else:
        return "Error retrieving data from NHL API."

    # Extract the relevant data from the JSON response
    games = []
    for game in data["dates"][0]["games"]:
        game_data = {}
        game_data["game_id"] = game["gamePk"]
        game_data["season"] = game["season"]
        game_data["type"] = game["gameType"]
        game_data["start_time"] = game["gameDate"]
        game_data["current_period"] = game["linescore"].get("currentPeriodOrdinal", 0)
        game_data["power_play"] = game["linescore"]["powerPlayStrength"]
        game_data["time_remaining_in_period"] = game["linescore"].get("currentPeriodTimeRemaining", 0)
        game_data["home_team"] = {
            "name": game["teams"]["home"]["team"]["name"],
        }
        game_data["away_team"] = {
            "name": game["teams"]["away"]["team"]["name"],
        }
        game_data["home_team_stats"] = {
            "goals": game["linescore"]["teams"]["home"]["goals"],
            "shots_on_goal": game["linescore"]["teams"]["home"]["shotsOnGoal"],
            # "power_play_goals": game["linescore"]["teams"]["home"]["powerPlayGoals"],
            # "power_play_opportunities": game["linescore"]["teams"]["home"]["powerPlayOpportunities"]
        }
        game_data["away_team_stats"] = {
            "goals": game["linescore"]["teams"]["away"]["goals"],
            "shots_on_goal": game["linescore"]["teams"]["away"]["shotsOnGoal"],
            # "power_play_goals": game["linescore"]["teams"]["away"]["powerPlayGoals"],
            # "power_play_opportunities": game["linescore"]["teams"]["away"]["powerPlayOpportunities"]
        }
        game_data["scoring_plays"] = []
        for play in game["scoringPlays"]:
            scoring_play = {}
            scoring_play["scorer"] = play["players"][0]["player"]["fullName"]
            scoring_play["assists"] = []
            for assist in play["players"][1:-1]:
                scoring_play["assists"].append(assist["player"]["fullName"])
            scoring_play["time"] = play["about"]["periodTime"]
            scoring_play["period"] = play["about"]["period"]
            scoring_play["period_type"] = play["about"]["periodType"]
            scoring_play["shot_type"] = play["result"].get("secondaryType", "")
            scoring_play["strength"] = play["result"]["strength"]["name"]
            scoring_play["score_after_goal"] = {
                "home": play["about"]["goals"]["home"],
                "away": play["about"]["goals"]["away"]
            }
            game_data["scoring_plays"].append(scoring_play)
        games.append(game_data)

    # Convert the data to JSON
    json_data = json.dumps(games)

    # Return the JSON data
    return jsonify(json.loads(json_data))

if __name__ == '__main__':
    app.run()

