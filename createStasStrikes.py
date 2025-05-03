import psycopg2
import argparse
import re
import pandas as pd
import os
from tabulate import tabulate

class Stats():  
    def __init__(self):
        super().__init__() 
        print("Create Stats Strikes")
        self.WhiteGame = []
        self.BlackGame = []
        self.game_id = ''
        self.query = ''
        self.username = ''

    def parseARgs(self):
        parser = argparse.ArgumentParser(description='statitisque player chessStrike')
        parser.add_argument("-u", "--username", action="store", default = 'marinmarin1950',
                        help="chesscom user Name")
        args = parser.parse_args()
        self.username = args.username

    def connectDb(self):
        self.postgresDB = psycopg2.connect(database="ChessAnalyse", user='chess', password='VerySecretAwx', host='192.168.1.123', port= '32352')

    def closeDb(self):
        self.postgresDB.close()

    def executeSql(self, type :str = 'None'):
        cursor = self.postgresDB.cursor()
        try:
            cursor.execute(self.query)
            if type == 'select': self.selectFetchDb = cursor.fetchall() 
        except Exception as err:
            print(f'Warning error bypass \n{err}')
            self.postgresDB.rollback()
        else:
            cursor.execute("COMMIT") 
        cursor.close()
    
    def calculDelay(self, string: str):
        list = string.split(':')
        sec = ( int(list[0]) * 60 ) + int(list[1]) + (float(list[2]) / 100)
        return sec

    def createStrikeTable(self):
        # init table stats
        self.query = f'DROP TABLE IF EXISTS public."{self.username}"'
        self.executeSql()
    
        self.query = f'CREATE TABLE IF NOT EXISTS public."{self.username}"'
        self.query += f'(id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9999999999999999 CACHE 1 ),'
        self.query += f'archive_id bigint NOT NULL,'
        self.query += f'strike_number integer NOT NULL, winner character varying(20) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'strike character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'player_color character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'response character varying(10) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'delay numeric(6,1) NOT NULL, game_id bigint NOT NULL,'
        self.query += f'player_name character varying(20) COLLATE pg_catalog."default" NOT NULL,'
        self.query += f'CONSTRAINT "{self.username}_pkey" PRIMARY KEY (id))' 
        self.query += f'TABLESPACE pg_default;'
        self.executeSql()

        self.query = f'ALTER TABLE IF EXISTS public."{self.username}"'
        self.query += f'OWNER to chess;'
        self.executeSql()

    def getStrikeWhite(self):
        # get gamed_id
        self.query = f'select COALESCE(max(game_id),0) from public."{self.username}"'
        self.executeSql(type = 'select')
        self.game_id = self.selectFetchDb[0][0]

        #get totalStrikes when white
        self.query = f"select strikes->'strikes'->0, color, strikes->'winner', id from public.\"games\" "
        self.query += f"where playername = '{self.username}' and color = 'White' "
        self.query += f"and color != strikes->>'winner' "
        self.executeSql(type = 'select')
        self.WhiteGame = self.selectFetchDb

    def getStrikeBlack(self):
        # get gamed_id
        self.query = f'select COALESCE(max(game_id),0) from public."{self.username}"'
        self.executeSql(type = 'select')
        self.game_id = self.selectFetchDb[0][0]

        #get totalStrikes when white
        self.query = f"select strikes->'strikes'->0, color, strikes->'winner', id from public.\"games\" "
        self.query += f"where playername = '{self.username}' and color = 'Black' "
        self.query += f"and color != strikes->>'winner' "
        self.executeSql(type = 'select')
        self.BlackGame = self.selectFetchDb
    
    def populateStrike(self, color :str):
        if color == 'White' :
            strikes = self.WhiteGame
        else:
            strikes = self.BlackGame
        count = 0
        for row in strikes:
            count += 1
            pattern= '^(\d+)\. ([\w\-\+\#\=]+) ([\w\-\+\#\=]+)'
            if row[0] is None: continue

            if re.match(pattern, row[0] ):
                strike_number = re.sub(pattern,'\\1',row[0])
                strike = re.sub(pattern,'\\2',row[0])
                response = re.sub(pattern,'\\3',row[0])
                tmp = "0:00:00.0"

            delay = self.calculDelay(tmp)
            delay = round(delay,1)           
            player_color = row[1]
            winner = self.username if row[2] == player_color else 'opponnent'
            archive_id = row[3]
            if int(strike_number) == 1 : self.game_id += 1 
            self.query = f'insert into public."{self.username}" '
            self.query += f'( strike_number, strike, player_color, response, delay, game_id, player_name, winner, archive_id ) '
            self.query += f'values '
            self.query += f"({strike_number}, \'{strike}\', \'{player_color}\', \'{response}\', \'{delay}\', {self.game_id }, \'{self.username}\', \'{winner}\', {archive_id})"
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
    initStat.closeDb()
