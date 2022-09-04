import json
import pandas as pd
from urllib.request import urlopen
import json
import pulp
import numpy as np

teams = pd.read_csv('teams.csv')
url = "https://fantasy.premierleague.com/api/bootstrap-static/"

def get_fdr(team_url):
  response = urlopen(team_url)
  data = json.loads(response.read())
  fdr_av = [6-data['fixtures'][0]['difficulty'],6-data['fixtures'][1]['difficulty'],6-data['fixtures'][2]['difficulty']]
  return sum(fdr_av) / len(fdr_av)

def get_stats(url,teams):
  response = urlopen(url)
  data_json = json.loads(response.read())
  data = data_json['elements']
  id,name,team_code,ppg,ict,fdr,price,pos,score= [],[],[],[],[],[],[],[],[]
  for i in data:
    id.append(i['id'])
    name.append(i['web_name'])
    team_code.append(i['team'])
    ppg.append(i['points_per_game'])
    ict.append(i['ict_index'])
    inv_fdr = get_fdr(teams['Link'][i['team']-1])
    fdr.append(inv_fdr)
    price.append(i['now_cost']/10)
    pos.append(i['element_type'])
    score.append((float(i['points_per_game'])*10+float(i['ict_index'])+float(inv_fdr)*20)/3)
  df = pd.DataFrame(list(zip(id,name,team_code,ppg,ict,fdr,price,pos,score)),
                    columns =['Player_ID','Name','Team_code','Point_per_game','ICT_index','Inv_FDR','Price','Pos_code','Score_index'])

  return df

def get_data(url,teams):
  response = urlopen(url)
  data_json = json.loads(response.read())
  data = data_json['elements']
  id,name,team,pos,form,photo,point,goal,assist,clean,selected,dream, latest= [],[],[],[],[],[],[],[],[],[],[],[],[]
  for i in data:
    id.append(i['id'])
    name.append(i['web_name'])
    team_no = i['team']
    team.append(teams['Team'][team_no-1])
    position = {1:'GKP',2:'DEF',3:'MID',4:'FWD'}
    pos.append(position[i['element_type']])
    form.append(i['form'])
    photo.append(i['photo'])
    point.append(i['total_points'])
    goal.append(i['goals_scored'])
    assist.append(i['assists'])
    clean.append(i['clean_sheets'])
    selected.append(i['selected_by_percent'])
    dream.append(i['in_dreamteam'])
  df = pd.DataFrame(list(zip(id,name,team,pos,form,photo,point,goal,assist,clean,selected,dream)),
                    columns =['Player_ID','Name','Team','Position','Form','Photo','Total_Points','Goals','Assists','Clean_Sheets','Selected','Dreamteam'])
  return df

from datetime import date
today = date.today()
def update_data():
  df = get_data(url,teams)
  dff = get_stats(url,teams)
  df['Latest_update'] = today.strftime("%b-%d-%Y")
  df.to_csv('fpldata.csv',index=False)
  dff.to_csv('fplstats.csv', index=False)
  return df['Latest_update'][0]


def select_team(expected_scores, prices, positions, clubs):
    num_players = len(expected_scores)
    model = pulp.LpProblem("Constrained value maximisation", pulp.LpMaximize)
    decisions = [
      pulp.LpVariable("x{}".format(i), lowBound=0, upBound=1, cat='Integer')
      for i in range(num_players)
    ]
    captain_decisions = [
      pulp.LpVariable("y{}".format(i), lowBound=0, upBound=1, cat='Integer')
      for i in range(num_players)
    ]

    # objective function:
    model += sum((captain_decisions[i] + decisions[i]) * expected_scores[i]
                 for i in range(num_players)), "Objective"

    # cost constraint
    model += sum(decisions[i] * prices[i] for i in range(num_players)) <= 100  # total cost
    model += sum(decisions) == 15  # total team size

    # position constraints
    # 1 goalkeeper
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 1) >= 1
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 1) <= 2
    # 3-5 defenders
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 2) >= 3
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 2) <= 5
    # 3-5 midfielders
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 3) >= 3
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 3) <= 5
    # 1-3 attackers
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 4) >= 1
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 4) <= 3

    # club constraint
    for club_id in np.unique(clubs):
      model += sum(decisions[i] for i in range(num_players) if clubs[i] == club_id) <= 3  # max 3 players

    model += sum(captain_decisions) == 1  # 1 captain

    for i in range(num_players):  # captain must also be on team
      model += (decisions[i] - captain_decisions[i]) >= 0

    model.solve()
    return decisions, captain_decisions

def select_subs(expected_scores, prices, positions, clubs):
    num_players = len(expected_scores)
    model = pulp.LpProblem("Constrained value maximisation", pulp.LpMinimize)
    decisions = [
      pulp.LpVariable("x{}".format(i), lowBound=0, upBound=1, cat='Integer')
      for i in range(num_players)
    ]
    captain_decisions = [
      pulp.LpVariable("y{}".format(i), lowBound=0, upBound=1, cat='Integer')
      for i in range(num_players)
    ]

    # objective function:
    model += sum((decisions[i]) * prices[i]
                for i in range(num_players)), "Objective"

    # cost constraint
    # model += sum(decisions[i] * prices[i] for i in range(num_players)) <= 100  # total cost
    model += sum(decisions) == 4  # total team size

    # position constraints
    # 1 goalkeeper
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 1) == 1
    # 3-5 defenders
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 2) >= 0
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 2) <= 1
    # 3-5 midfielders
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 3) >= 0
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 3) <= 1
    # 1-3 attackers
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 4) >= 0
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 4) <= 1

    # club constraint
    for club_id in np.unique(clubs):
      model += sum(decisions[i] for i in range(num_players) if clubs[i] == club_id) <= 3  # max 3 players

    model.solve()
    return decisions

def select_main(expected_scores, prices, positions, clubs, subbudget,df,mid,fw):
    num_players = len(expected_scores)
    model = pulp.LpProblem("Constrained value maximisation", pulp.LpMaximize)
    decisions = [
      pulp.LpVariable("x{}".format(i), lowBound=0, upBound=1, cat='Integer')
      for i in range(num_players)
    ]
    captain_decisions = [
      pulp.LpVariable("y{}".format(i), lowBound=0, upBound=1, cat='Integer')
      for i in range(num_players)
    ]

    # objective function:
    model += sum((captain_decisions[i] + decisions[i]) * expected_scores[i]
                 for i in range(num_players)), "Objective"

    # cost constraint
    model += sum(decisions[i] * prices[i] for i in range(num_players)) <= (100-subbudget)  # total cost
    model += sum(decisions) == 11  # total team size

    # position constraints
    # 1 goalkeeper
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 1) == 1
    # 3-5 defenders
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 2) >= 2
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 2) <= 4
    # 3-5 midfielders
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 3) >= 2
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 3) <= 4
    # 1-3 attackers
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 4) >= 1
    model += sum(decisions[i] for i in range(num_players) if positions[i] == 4) <= 2

    # club constraint
    for club_id in np.unique(clubs):
      model += sum(decisions[i] for i in range(num_players) if clubs[i] == club_id) <= 3  # max 3 players

    model += sum(captain_decisions) == 1  # 1 captain

    for i in range(num_players):  # captain must also be on team
      model += (decisions[i] - captain_decisions[i]) >= 0

    model.solve()
    return decisions, captain_decisions


