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
        self.filter = None
        self.initFilter = None

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
        self.query = f'select distinct count(*), strike_number, strike, response from public."{self.username}" '
        self.query += f'where winner = \'opponnent\' and player_color = \'{self.color}\' '
        if self.initFilter is not None: 
            self.query += f"and strike like '%{self.initFilter}%' " if self.color == 'White' else f"and response like '%{self.initFilter}%' "
        self.query += f'group by strike, response, strike_number order by 1 desc'
        self.executeSql()
        self.firstStrikeCandidate = self.selectFetchDb

    def roadmapWins(self):
        csv = open('/tmp/roadmap.csv','w')
        csv.write(f'number of defeat;player_name;player_color;step;strike;response;next possible Strike;next_wining;next wining_response\n')
            
        tmp = []   
        for strike in self.firstStrikeCandidate : 
            self.query = f"select distinct count(*), strikes->'strikes'->>{strike[1]} as seq from public.\"games\" "
            self.query += f"where playername = '{self.username}' "
            if strike[1] == 1 :
                self.query += f"and strikes->'strikes'->>{strike[1]-1}  like '%{strike[1]}. {strike[2]}%{strike[3]}%' "
            else:
                winStrike = self.filter.split(' ')
                self.query += f"and strikes->'strikes'->>{strike[1]-1}  like '%{strike[1]}. {winStrike[0]}%{winStrike[1]}%' "     
            self.query += f"and color != strikes->>'winner' "
            self.query += f'and id in ( select archive_id from public."{self.username}" '
            self.query += f'where winner = \'opponnent\' and player_color = \'{self.color}\' and '
            self.query += f"strike like '{self.initFilter}' ) " if self.color == 'White' else f"response like '{self.filter}' ) "
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
            
                tmp.append((next[0],int(nextStep),nextStrike,nextResponse))
                csv.write(f'{strike[0]};{self.username};{self.color};{strike[1]};{strike[2]};{strike[3]};{nextStep};{nextStrike};{nextResponse}\n')

        csv.close()
        self.firstStrikeCandidate = tmp
        return len(self.roadmap)

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
        print(f'########## Tape next wining strike again {prediction.username} with {prediction.color} ?')
        self.filter = input('example g3 d5 default (None): ').strip() or None

if __name__ == "__main__" :

    prediction = Predictive()
    prediction.parseARgs()
    print(f'########## Tape a filter first strike for {prediction.username} with {prediction.color} ?')
    prediction.initFilter = input('example e4 default (None): ').strip() or None
    prediction.connectDb()
    prediction.candidateStrike()
    ended = prediction.roadmapWins()
    while ended > 0:
        prediction.displayRoadMap()
        ended = prediction.roadmapWins()
    prediction.deleteCache()
    prediction.closeDb()

