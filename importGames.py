from urllib.request import urlopen
import json
import re
import psycopg2
from pgn_parser import pgn, parser
import sys

def read(url: str ):
    response = None
    body = {}
    try: 
        response = urlopen(url) 
    except Exception as Err:
        body['erreur'] = Err
    else:
        body['content'] = response.read()
    finally:
        if response is not None:
            response.close()
        return body

def getArchives(urls: list ):
    response = None
    body = {}
    archives = json.loads(urls)
    body['archiveGames'] = {}
    for url in archives['archives']:
        date = re.sub('^https://(.*)/games/(\d+)/(\d+)','\\2-\\3',url)
        try:
            response = read(url) 
        except Exception as Err:
            body['erreur'] = Err
        else:
            body['archiveGames'].update({ date: url })
    return body

def convertPgn(data: str):
    data = re.sub('\d+\.\.\.','',data)
    jsonDict = {}
    values = []
    try:
      games = parser.parse(data, actions=pgn.Actions())
    except:
        jsonDict['status'] = 'KO'
        return json.dumps(jsonDict)
    chessComAdvise = games.tag_pairs['Link']
    strikes = games.movetext
    jsonDict['totalStrikes'] = len(games.movetext)

    for value in strikes:
        values.append(str(value))
    
    jsonDict['strikes'] = values
    jsonDict['winner'] = 'White' if games.score.white == 1 else 'Black'
    jsonDict['status'] = 'OK'
    jsonDict['chesscomadvice'] = chessComAdvise
    return json.dumps(jsonDict)


def insertPngValue(urls: dict, user: str ):
    conn = psycopg2.connect(database="ChessAnalyse", user='chess', password='VerySecretAwx', host='192.168.1.123', port= '32352')
    for date, url in urls['archiveGames'].items() :
        cursor = conn.cursor()
        year, month = date.split('-')     

        data = json.loads(read(url)['content'].decode())
        for values in data['games']:
            color = 'White' if values['white']['username'].lower() == user else 'Black'
            if values['rules'] == 'chess':
                pgnData = values['pgn']   
                jsonData = convertPgn(pgnData)      
                dictData = json.loads(jsonData)      
                if dictData['status'] != 'KO' : 
                    query = f"insert into games( playername, color, strikes, year, month, chesscomadvice ) "
                    query += f"values ( '{user}', '{color}', '{jsonData}', {year}, {month}, '{dictData['chesscomadvice']}' )"
                    try:
                        cursor.execute(query)
                    except psycopg2.IntegrityError as err:
                        print(f'Warning error bypass \n{err}')
                        conn.rollback()
                    else:
                        cursor.execute("COMMIT") 
    conn.close()


def getIdUser(data: str):
    jsonData = json.loads(data)
    return jsonData['username']
    
if __name__ == "__main__" :
    url = f"https://api.chess.com/pub/player/{sys.argv[1]}"
    #url = f"https://api.chess.com/pub/player/diegiton"
    data = read(url)
    username = getIdUser(data['content'])
    url = f'https://api.chess.com/pub/player/{username}/games/archives'
    archivesGamesUrl = read(url)
    archivesGames = getArchives(archivesGamesUrl['content'])
    insertPngValue(urls = archivesGames , user = username)
    

