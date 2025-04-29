import psycopg2
import argparse
import re

class Stats():  
    def __init__(self):
        super().__init__() 
        print("Predictive Strikes")
        self.WhiteGame = []
        self.BlackGame = []
        self.query = ''

    def parseARgs(self):
        parser = argparse.ArgumentParser(description='statitisque player chessStrike')
        parser.add_argument("-u", "--username", action="store", default = 'diegiton',
                        help="chesscom user Name")
        args = parser.parse_args()
        self.username = args.username

    def connectDb(self):
        self.postgresDB = psycopg2.connect(database="ChessAnalyse", user='chess', password='VerySecretAwx', host='192.168.1.123', port= '32352')

    def executeSql(self, type :str = 'None'):
        cursor = self.postgresDB.cursor()
        try:
            cursor.execute(self.query)
            if type == 'select': self.selectFetchDb = cursor.fetchall() 
        except psycopg2.IntegrityError as err:
            print(f'Warning error bypass \n{err}')
            self.postgresDB.rollback()
        else:
            cursor.execute("COMMIT") 
        cursor.close()

    def strMultipleReplace(self, string: str, replace: list):
        for exp,rep in replace:
            string = re.sub(exp,rep,string)
        return string
    
    def calculDelay(self, string: str):
        list = string.split(':')
        sec = ( int(list[0]) * 60 ) + int(list[1]) + (float(list[2]) / 100)
        return sec



    def createStrikeTable(self):
        # init table stats
        self.query = f'DROP TABLE IF EXISTS public."strikesStats"'
        self.executeSql()
    
        self.query = f'CREATE TABLE IF NOT EXISTS public."strikesStats"'
        self.query += f'(id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9999999999999999 CACHE 1 ),'
        self.query += f'archive_id bigint NOT NULL,'
        self.query += f'strike_number integer NOT NULL, winner character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'strike character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'player_color character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'response character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'delay numeric(6,1) NOT NULL, game_id bigint NOT NULL,'
        self.query += f'player_name character varying(20) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'CONSTRAINT "strikesStats_pkey" PRIMARY KEY (id))' 
        self.query += f'TABLESPACE pg_default;'
        self.executeSql()

        self.query = f'ALTER TABLE IF EXISTS public."strikesStats"'
        self.query += f'OWNER to chess;'
        self.executeSql()

    def getStrikeWhite(self):
        # get gamed_id
        self.query = f'select COALESCE(max(game_id),0) from public."strikesStats"'
        self.executeSql(type = 'select')
        self.game_id = self.selectFetchDb[0][0]

        #get totalStrikes when white
        self.query = f"select jsonb_array_elements(strikes->'strikes'), color, strikes->'winner', id from public.\"games\" where playername = '{self.username}' and color = 'White'"
        self.executeSql(type = 'select')
        self.WhiteGame = self.selectFetchDb

    def getStrikeBlack(self):
        # get gamed_id
        self.query = f'select COALESCE(max(game_id),0) from public."strikesStats"'
        self.executeSql(type = 'select')
        self.game_id = self.selectFetchDb[0][0]

        #get totalStrikes when white
        self.query = f"select jsonb_array_elements(strikes->'strikes'), color, strikes->'winner', id from public.\"games\" where playername = '{self.username}' and color = 'Black'"
        self.executeSql(type = 'select')
        self.BlackGame = self.selectFetchDb
    
    def populateStrike(self, color :str):
        if color == 'White' :
            strikes = self.wWiteGame
        else:
            strikes = self.BlackGame
        count = 0
        for row in self.whiteGame :
            count += 1
            pattern= '^(\d+)\. ([\w\-\+\#\=]+) {\[%clk (.*)\]} ([\w\-\+\#\=]+) {\[%clk (.*)\]}'
            patternMate= '^(\d+)\. ([\w\-\+\#\=]+) {\[%clk (.*)\]}(.*)'

            if re.match(pattern, row[0] ):
                strike_number = re.sub(pattern,'\\1',row[0])
                strike = re.sub(pattern,'\\2',row[0])
                response = re.sub(pattern,'\\4',row[0])
                tmp = re.sub(pattern,'\\3',row[0])
            elif re.match(patternMate, row[0] ):
                strike_number = re.sub(patternMate,'\\1',row[0]) 
                strike = re.sub(patternMate,'\\2',row[0]) if row[1] == row[2] else 'Mate'
                response = re.sub(patternMate,'\\2',row[0]) if row[1] != row[2] else 'Mate'
                tmp = re.sub(patternMate,'\\3',row[0])    
            else:
                pass

            delay = self.calculDelay(tmp)
            delay = round(delay,1)           
            player_color = row[1]
            winner = {self.username} if row[2] == player_color else 'opponnent'
            archive_id = row[3]
            if int(strike_number) == 1 : self.game_id += 1 
            self.query = f'insert into public."strikesStats" '
            self.query += f'( strike_number, strike, player_color, response, delay, game_id, player_name, winner, archive_id ) '
            self.query += f'values '
            self.query += f"({strike_number}, '{strike}', '{player_color}', '{response}', '{delay}', {self.game_id }, '{self.username}', '{winner}', {archive_id})"
            self.executeSql()

if __name__ == "__main__" :
    initStat = Stats()
    initStat.parseARgs()
    initStat.connectDb()
    initStat.createStrikeTable()
    initStat.getStrikeWhite()
    initStat.getStrikeBlack()
    initStat.populateStrike(color = 'White')
    initStat.populateStrike(color = 'Black')
