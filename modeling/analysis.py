import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression

def clean_player_entry(entry):
    player_list = entry.split(",")[:-1]
    player_list = [player.strip(" ") for player in player_list ]
    assert len(player_list) == 7, f"{entry} doesn't have 7 players"
    return player_list

#%% Constants
FLYERS_ID = 242

we_score = ['GOAL', 'CALLAHAN']
they_score = ['SCORED_ON', 'CALLAHAN_THROWN']
line_sets = ['SET_D_LINE', 'SET_O_LINE', 'SET_D_LINE_NO_PULL', 'SET_O_LINE_NO_PULL']
line_sets_offense = ['SET_O_LINE', 'SET_O_LINE_NO_PULL']

#%% Read data
df = pd.read_csv("Flyers_Games_220729.csv", index_col=0, dtype={"line": object})
df["game_point_id"] = df["game_id"]*1000 + df["point_id"]

#%% Get team rosters and dataframe of all players
team_rosters = {}
for team_id in df.team_id.unique():
    lines = df[(df.line.notnull()) & (df.team_id == team_id)]
    players = set()
    
    chars_to_remove = ["[","]","\"", "" ]
    
    for _, row in lines.iterrows():
        players_list = row["line"].split("'")[1::2][:-1]
        players = players.union(players_list)
    
    team_rosters[team_id] = players

records = []
for team_id, roster in team_rosters.items():
    for player in roster:
        record = (player, team_id)
        records.append(record)
all_players = pd.DataFrame.from_records(records, columns = {"player", "team_id"})
all_players = all_players.reset_index().set_index("player")

#%% Gather data needed for model-fitting
flyers_goals = df[(df.event_type.isin(we_score)) & (df.team_id == FLYERS_ID)][["game_point_id","event_counter"]]
flyers_goals["is_final"] = True
del flyers_goals["event_counter"]

flyers_line_sets = df[(df.event_type.isin(line_sets)) & (df.team_id == FLYERS_ID)]

data = flyers_line_sets[["game_point_id", "player", "event_counter", "event_type"]].copy()
data["is_offense"] = data["event_type"].isin(line_sets_offense)
data["player"] = data["player"].apply(clean_player_entry)

max_event = data.groupby("game_point_id")["event_counter"].transform(max).values
data["is_final"] = data.event_counter == max_event

data = data.merge(flyers_goals, how="left", on=["game_point_id", "is_final"], indicator=True)
data["score"] = data._merge == "both"
del data["_merge"]

#%% Create training data
flyers_roster = list(team_rosters[FLYERS_ID])
player_to_idx = {name : idx for idx, name in enumerate(flyers_roster)}

num_players = len(flyers_roster)
num_lines = len(data)

X = np.zeros((num_lines, num_players+1), dtype=bool)
y = data["score"].values

for line_idx, (_, row) in enumerate(data.iterrows()):
    for player_name in row["player"]:
        player_idx = player_to_idx[player_name]
        X[line_idx, player_idx] = 1
    if row["is_offense"]:
        X[line_idx, -1] = 1

#%% Fit model
clf = LogisticRegression(random_state=0, C=0.1, penalty="l1", solver="liblinear").fit(X, y)
probs = clf.predict_proba(X)
print(clf.score(X,y))

player_scores = pd.DataFrame({"player": flyers_roster, "points": X[:,:-1].sum(axis=0), "score": clf.coef_[0][:-1]})
player_scores.sort_values("score", inplace=True)
print(player_scores)
print(f"Offensive coefficient: {clf.coef_[0][-1]:0.3f}")