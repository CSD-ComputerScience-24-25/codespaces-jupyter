import sqlite3

class DB ():
    def __init__(self):
        self.db = "TheBlueDB.sqlite"

    def check_team(self, team_key):
        return False
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(f"SELECT team_key FROM Teams where team_key = {team_key}")
        print(cur.fetchone)
        return(team_key == cur.fetchone)

    def checkEvent(event_key):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        pass

    def updateTeams(team_key, city,country, ):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        pass

    def udpateEvents(event_key):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        pass

    def get_team(crawler, team_key):
        return False

    def add_team(team_key, city, country, nickname, postal_code, rookie_year, school_name, state_prov, team_number, website):
        pass

    
