import requests
import json

class TBA_Crawler():
    def __init__(self):
        self.AuthKey = "GFrcbI73XcLc57dkNTHUJUtnf9GBLg8PISQQ2iHpBejVJ0Ch7HYfV3N29STFBo1Z"

    def getTeamEvents(year: str, team_key: str, self) -> str:
        api_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}"
        params = {"X-TBA-Auth-Key": self.AuthKey, "H":"accept: application/json"}

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            #parsed = json.loads(data)

            formatted = json.dumps(data, indent=4)
            #print(formatted)
            return formatted
    
    def getEventMatches(team_key: str, event_key: str, self) -> str:
        api_url = f'https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches'
        params = {"X-TBA-Auth-Key": self.AuthKey, "H":"accept: application/json"}

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            #parsed = json.loads(data)

            formatted = json.dumps(data, indent=4)
            #print(formatted)
            return formatted
    
    def getTeamInfo():
        api_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}"


        