import psycopg2
import argparse
import re
import pandas as pd
import os
from tabulate import tabulate

class Predictive():
    def __init__(self):
        super().__init__() 
        print("Find Predictive Strikes")    
        self.query = ''
        self.initFilter = None
        self.history = []
        self.countStrike = 0

    def connectDb(self):
        self.postgresDB = psycopg2.connect(database="ChessAnalyse", user='chess', password='VerySecretAwx', host='192.168.1.123', port= '32352')

    def closeDb(self):
        self.postgresDB.close()
    
    def deleteCache(self):
        os.remove('/tmp/roadmap.csv')

    def parseARgs(self):
        parser = argparse.ArgumentParser(description='statitisque player chessStrike')
        parser.add_argument("-u", "--username", action="store", default = 'marinmarin1950',
                        help="chesscom user Name")
        parser.add_argument("-c", "--color", action="store", default = 'White',
                        help="White or Black for user color")
        args = parser.parse_args()
        self.username = args.username
        self.color = args.color

    def candidateStrike(self):
        #request the de defeat games for opponnent
        self.query = f'select distinct count(*), strike_number, strike, response from public."{self.username}" '
        self.query += f'where winner = \'opponnent\' '
        if self.initFilter is not None: 
            self.query += f"and strike like '%{self.initFilter}%' "
        self.query += f'group by strike, response, strike_number order by 1 desc'
        self.executeSql()
        
        #display the result
        print(f'########## Tape first strike for white in preditictive {prediction.username} Game :')
        self.initFilter = input('example e4 default (None): ').strip() or None
        csv = open('/tmp/roadmap.csv','w')
        csv.write(f'number of defeat;player_name;player_color;step;strike;response\n')
        for row in self.selectFetchDb:
            csv.write(f'{row[0]};{self.username};{self.color};{row[1]};{row[2]};{row[3]}\n')
        csv.close()
        print(tabulate(pd.read_csv('/tmp/roadmap.csv', sep='[;]', parse_dates=True),headers="keys", tablefmt="grid",showindex=False,maxcolwidths=[None, 20]))
        print(f'########## select first response Black in predictive {prediction.username} Game :')
        self.initFilter += ' '
        self.initFilter += input('example d5 default (None): ').strip() or None
        self.history.append(self.initFilter)

        #request the de defeat games for opponnent for roadmap
        strike, response = self.initFilter.split( )
        self.query = f'select distinct count(*), strike_number, strike, response from public."{self.username}" '
        self.query += f'where winner = \'opponnent\' '
        if self.initFilter is not None: 
            self.query += f"and strike like '%{strike}%' and response like '%{response}%' "
        self.query += f'group by strike, response, strike_number order by 1 desc'
        self.executeSql()
        self.firstStrikeCandidate = self.selectFetchDb
        self.ended = 1

    def roadmapWins(self):
        csv = open('/tmp/roadmap.csv','w')
        csv.write(f'number of defeat;player_name;player_color;step;strike;response;next possible Strike;next_wining;next wining_response\n')
            
        for strike in self.firstStrikeCandidate : 
            self.query = f"select distinct count(*), strikes->'strikes'->>{self.countStrike+1} as seq from public.\"games\" "
            self.query += f"where playername = '{self.username}' "

            for index in range(len(self.history)):
                winStrike = self.history[index].split(' ')
                self.query += f"and strikes->'strikes'->>{index}  like '%{index+1}. {winStrike[0]}%{winStrike[1]}%' "     

            self.query += f"and color != strikes->>'winner' "
            self.query += f"group by seq order by 1 desc"
            self.executeSql()
            self.roadmap = self.selectFetchDb


            for next in self.roadmap:
                if next[1] is None:
                    continue
                elif re.match('^(\d+). ([\w\-\+\#\=]+) ([\w\-\+\#\=]+)',next[1]):
                    nextStep = re.sub('^(\d+)\. ([\w\-\+\#\=]+) ([\w\-\+\#\=]+)','\\1',next[1])
                    nextStrike =  re.sub('^(\d+)\. ([\w\-\+\#\=]+) ([\w\-\+\#\=]+)','\\2',next[1])
                    nextResponse = re.sub('^(\d+)\. ([\w\-\+\#\=]+) ([\w\-\+\#\=]+)','\\3',next[1])
                else:
                    nextStep, nextStrike, nextResponse = next[1].split(' ')
                csv.write(f'{strike[0]};{self.username};{self.color};{strike[1]};{strike[2]};{strike[3]};{nextStep};{nextStrike};{nextResponse}\n')
        self.countStrike += 1
        csv.close()
        #self.firstStrikeCandidate = tmp
        self.ended = len(self.roadmap)

    def executeSql(self, type :str = 'None'):
        cursor = self.postgresDB.cursor()
        try:
            cursor.execute(self.query)
            self.selectFetchDb = cursor.fetchall() 
        except Exception as err:
            print(f'Warning error bypass \n{err}')
            self.postgresDB.rollback()
        else:
            cursor.execute("COMMIT") 
        cursor.close()
    
    def displayRoadMap(self):
        print(tabulate(pd.read_csv('/tmp/roadmap.csv', sep='[;]', parse_dates=True),headers="keys", tablefmt="grid",showindex=False,maxcolwidths=[None, 20]))
        print(f'########## Choose {self.countStrike} wining strike again {prediction.username} with {prediction.color} ?')
        self.initFilter = input('example g3 d5 default (None): ').strip() or None
        self.history.append(self.initFilter)

        self.query = f"select distinct count(*), strikes->'strikes'->>{self.countStrike} as seq from public.\"games\" "
        self.query += f"where playername = '{self.username}' "
        for index in range(len(self.history)):
            winStrike = self.history[index].split(' ')
            self.query += f"and strikes->'strikes'->>{index}  like '%{index+1}. {winStrike[0]}%{winStrike[1]}%' "     

        self.query += f"and color != strikes->>'winner' "
        self.query += f"group by seq order by 1 desc"
        self.executeSql()
        self.firstStrikeCandidate = []
        for row in self.selectFetchDb:
            tmp, strike, response = row[1].split(' ')
            strikeNumber = re.sub('^(\d+)\.','\\1',tmp)
            self.firstStrikeCandidate.append((row[0],strikeNumber,strike,response))

if __name__ == "__main__" :
    prediction = Predictive()
    prediction.parseARgs()
    prediction.connectDb()
    prediction.candidateStrike()
    while prediction.ended > 0:
        prediction.roadmapWins()
        prediction.displayRoadMap()
    prediction.deleteCache()
    prediction.closeDb()

