import requests
import json
import db

class TBA_Crawler():
    def __init__(self):
        self.AuthKey = "GFrcbI73XcLc57dkNTHUJUtnf9GBLg8PISQQ2iHpBejVJ0Ch7HYfV3N29STFBo1Z"
        self.db = db.DB()

    def getTeamEvents(self, team_key: str, year: str ):
        self.check_team(team_key)
        api_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}"
        params = {"X-TBA-Auth-Key": self.AuthKey, "H":"accept: application/json"}

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            #db.add_team()
            #print(data)
            #parsed = json.dumps(data, indent= 4)
            #print(parsed)
            return data
        else: print('No Response')
    
    def getEventMatches(self, team_key: str, event_key: str) -> str:
        api_url = f'https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches'
        params = {"X-TBA-Auth-Key": self.AuthKey, "H":"accept: application/json"}

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            #parsed = json.loads(data)

            formatted = json.dumps(data, indent=4)
            #print(formatted)
            return data
    
    def getTeamInfo(self, team_key):
        api_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}"
        params = {"X-TBA-Auth-Key": self.AuthKey, "H":"accept: application/json"}

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            #db.add_team()
            #print(data)
            parsed = json.dumps(data, indent= 4)
            #print(parsed)
            return data
        else: print('No Response')

    def check_team(self, team_key: str):
        if self.db.check_team(team_key):
            pass
        else:
            data = self.getTeamInfo(team_key)
            #print(data)
            self.db.add_team(data["key"],
                             data['city'],
                             data['country'],
                             data['nickname'],
                             data['postal_code'],
                             data['rookie_year'],
                             data['school_name'],
                             data['state_prov'],
                             data['team_number'],
                             data['website'])


        