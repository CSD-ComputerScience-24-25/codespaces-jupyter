import sqlite3

class DB ():
    def __init__(self):
        self.db = "TheBlueDB.sqlite"
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(f'CREATE TABLE IF NOT EXISTS "Teams" ("team_key" PRIMARY KEY NOT NULL UNIQUE, "city" TEXT, "country" TEXT, "nickname" TEXT, "postal_code" TEXT, "rookie_year" INTEGER, "school_name" TEXT, "state_prov" TEXT, "team_number" INTEGER, "website" TEXT)')


    def check_team(self, team_key):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(f'SELECT team_key FROM "Teams" WHERE "team_key" = {team_key}')
        print(cur.fetchone)
        return team_key == cur.fetchone()

    def checkEvent(self, event_key):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        pass

    def updateTeams(self, team_key, city,country, ):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        pass

    def udpateEvents(self, event_key):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        pass

    def get_team(crawler, team_key):
        return False

    def add_team(self, team_key, city, country, nickname, postal_code, rookie_year, school_name, state_prov, team_number, website):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(f'INSERT "Teams" (team_key, city, country, nickname, postal_code, rookie_year, school_name, state_prov, team_number, website) VALUES ({team_key},{city},{country},{nickname}, {postal_code}, {rookie_year},{school_name},{state_prov},{team_number}, {website})')

    
