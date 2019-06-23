import requests
import json
import pandas

#load live json from mls website
players = requests.get(url='https://fgp-data-us.s3.amazonaws.com/json/mls_mls/players.json').json()
squads = requests.get(url='https://fgp-data-us.s3.amazonaws.com/json/mls_mls/squads.json').json()
rounds = requests.get(url='https://fgp-data-us.s3.amazonaws.com/json/mls_mls/rounds.json').json()

#write json to txt file for manual parsing 
with open('players.txt', 'w') as outfile:  
    json.dump(players, outfile)
with open('squads.txt', 'w') as outfile:  
    json.dump(squads, outfile)	
with open('rounds.txt', 'w') as outfile:  
    json.dump(rounds, outfile)

i = 1
for player in players:
	print i, player["last_name"], player["first_name"]
	i = i+1