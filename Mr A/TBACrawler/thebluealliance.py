import requests
import json
import tbacrawler

team_number = input("Enter a team number: ")
tba = tbacrawler.TBA_Crawler()
team_key = 'frc' + team_number
year = '2024'
api_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}"
params = {"X-TBA-Auth-Key": "GFrcbI73XcLc57dkNTHUJUtnf9GBLg8PISQQ2iHpBejVJ0Ch7HYfV3N29STFBo1Z", "H":"accept: application/json"}

data = tba.getTeamEvents(team_key, year)
#formated = json.dumps(data, indent=4)
print(data)
for event in data:
    event_name = event['name']
    event_key = event['key']
    matches = tba.getEventMatches(team_key, event_key)
    #print(json.dumps(matches, indent= 4))

    for match in matches:
        blue_teams = match['alliances']['blue']['team_keys']
        blue_team_score = match['alliances']['blue']["score"]
        red_teams = match['alliances']['red']['team_keys']
        red_team_score = match['alliances']['red']['score']
        blue_teams_f = ''

        if match['comp_level'] == 'qm':
            match_type = "Qualification Match"
        else:
            match_type = "Elimination Match"

        print("\n",event_name, '-', match_type,
              match['match_number'])
        
        for i,team in enumerate(blue_teams):
            blue_teams[i] = blue_teams[i][3:]

        for i,team in enumerate(red_teams):
            red_teams[i] = red_teams[i][3:]
        print("Blue Alliance")
        print(blue_teams, 
              blue_team_score)
        print("Red Alliance")
        print(red_teams,
              red_team_score)
        
    