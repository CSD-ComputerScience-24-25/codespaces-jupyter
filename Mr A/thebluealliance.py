import requests
import json

team_key = 'frc9438'
year = '2024'
api_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}"
params = {"X-TBA-Auth-Key": "GFrcbI73XcLc57dkNTHUJUtnf9GBLg8PISQQ2iHpBejVJ0Ch7HYfV3N29STFBo1Z", "H":"accept: application/json"}

response = requests.get(api_url, params=params)


if response.status_code == 200:
    data = response.json()
    #parsed = json.loads(data)

    formatted = json.dumps(data, indent=4)
    print(formatted)


for event in data:
    event['name']
    event_key = event['key']
    
    api_url = f'https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches'
    response = requests.get(api_url, params=params)
    matches = response.json()
    print(json.dumps(matches, indent= 4))
    for match in matches:
        print(match['match_number'])
        print(match['blue']['team_keys'], match['blue']["score"])
        print(match['red']['team_keys'], match['red']['score'])
        
    